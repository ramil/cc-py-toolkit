# Data Migration Reference

## Migration Scope

### Master Data Objects
| Object | SAP Infotype | Source | Method | Validation |
|--------|-------------|--------|--------|------------|
| Personal Data | IT0002 | Legacy employee master | LSMW | Name, DOB, SSN match |
| Org Assignment | IT0001 | Legacy + SAP OM | LSMW | PA/PSA/EE Grp mapping |
| Addresses | IT0006 | Legacy address file | LSMW | Geocode resolution |
| Basic Pay | IT0008 | Legacy compensation | LSMW | Annual salary/rate match |
| Bank Details | IT0009 | Legacy direct deposit | LSMW | Routing + account verify |
| Recurring Ded/Payments | IT0014 | Legacy deductions | LSMW | Amount, start/end dates |
| Additional Payments | IT0015 | Legacy one-time pays | LSMW | Active records only |
| Residence Tax | IT0207 | Legacy address | LSMW | Zip → geocode |
| Work Tax Area | IT0208 | Legacy work site | LSMW | Tax authority mapping |
| Tax Withholding | IT0210 | Legacy W-4/state forms | LSMW | Filing status, allowances |
| Garnishments | IT0194/0195 | Legacy garnishment orders | LSMW | Court order details |
| Benefits Enrollment | IT0167/0168 | Legacy benefits data | LSMW | Plan/option mapping |

### YTD Balance Migration
| Object | SAP Infotype | Purpose | Critical Fields |
|--------|-------------|---------|----------------|
| Tax YTD Balances | IT0559 | Federal/state/local tax accumulators | Taxable gross, FIT, SIT, FICA, FUTA per authority |
| Prior Employment | IT0560 | Prior employer balances (mid-year only) | Used if employee had prior employer in same tax year |
| Absence Quotas | IT2006 | PTO/sick leave balances | Accrued, used, remaining balance |

## Hiring Data Migration File Template

### Purpose
The `/payroll-migration-file` command generates a pre-populated Excel file with sample employee records aligned to the configuration workbook. This provides:
- A ready-to-use LSMW/HRCM import template with correct field structures per infotype
- Sample employees covering all configured scenarios (exempt, non-exempt, union, multi-state, etc.)
- Pre-validated values that match the config workbook (org codes, wage types, tax authorities, benefit plans)
- Loading order guidance for infotype dependency management

### Infotype Sheet Structure (18 sheets)
| Sheet | Infotype | Description | Key Fields |
|-------|----------|-------------|------------|
| 1 | IT0000 | Actions | Action type (01=Hiring), reason, status |
| 2 | IT0001 | Org Assignment | Company code, PA, PSA, EE Group/Subgroup, payroll area, cost center |
| 3 | IT0002 | Personal Data | Name, DOB, gender, marital status, SSN |
| 4 | IT0006 | Addresses | Street, city, state, zip (aligned with tax authorities) |
| 5 | IT0007 | Planned Working Time | WSR, employment %, time mgmt status, planned hours |
| 6 | IT0008 | Basic Pay | Wage type, amount, pay scale (if applicable) |
| 7 | IT0009 | Bank Details | Bank key, account, payment method |
| 8 | IT0014 | Recurring Deductions | 401k, medical premiums, other deduction WTs |
| 9 | IT0207 | Residence Tax Area | Home state/county/city tax authority |
| 10 | IT0208 | Work Tax Area | Work location tax authority |
| 11 | IT0210 | Tax Withholding | Federal + state W-4 data per authority |
| 12 | IT0167 | Health Plans | Medical, dental, vision enrollment |
| 13 | IT0168 | Insurance Plans | Life, AD&D, STD, LTD coverage |
| 14 | IT0169 | Savings Plans | 401k contribution %, match reference |
| 15 | IT0171 | General Benefits | FSA, HSA elections |
| 16 | IT0194 | Garnishment Order | Court order details for test employees |
| 17 | IT0559 | Tax YTD Balances | Mid-year go-live YTD accumulators |
| 18 | IT2006 | Absence Quotas | PTO/sick leave opening balances |

### Employee Scenario Requirements
The migration file must include at least one employee per configured scenario:
- Salaried exempt (monthly/biweekly)
- Hourly non-exempt (biweekly/weekly with OT eligibility)
- Part-time (reduced schedule, pro-rated benefits)
- State-specific (CA with daily OT, multi-state worker)
- Union (CBA pay scale, union benefits) — if configured
- Executive (supplemental comp)
- Mid-year hire (prior employer YTD via IT0559/0560)
- Garnishment recipient (child support order)
- Shift worker (2nd/3rd shift differential) — if configured

### Validation Rules
Every value in the migration file must cross-reference to the config workbook:
- IT0001 org codes → Config Tab 1 (Enterprise Structure)
- IT0007 WSR codes → Config Tab 4 (Work Schedule Rules)
- IT0008 wage types → Config Tab 5 (Wage Type Catalog)
- IT0207/0208 tax areas → Config Tab 8 (Tax Authorities)
- IT0167-0171 benefit plans → Config Tab 14 (Benefits Config)
- IT0194 garnishment types → Config Tab 11 (Garnishment Config)
- IT0006 address state must match IT0207 residence tax state

## Migration Tools

### LSMW (Legacy System Migration Workbook)
- Standard SAP tool for batch data loads
- Steps: Define project → Define object → Map fields → Convert data → Load
- Transaction: LSMW
- Methods: Direct input, BAPI, IDoc, recording

### SAP HRCM (HR Conversion Manager)
- Specialized for HR master data migration
- Better handling of infotype sequencing and dependencies
- Pre-built templates for common HR infotypes
- Transaction: HRCM

### Best Practices
1. Load infotypes in dependency order: IT0000 → IT0001 → IT0002 → IT0006 → IT0007 → IT0008 → IT0009 → IT0207 → IT0208 → IT0210 → IT0014 → IT0015
2. Validate geocode resolution (IT0207/0208) before tax data (IT0210)
3. Run tax calculation test after IT0210 load to verify BSI integration
4. Load YTD balances (IT0559) after all master data is confirmed

## Parallel Run Design

### Purpose
Run payroll in both legacy and SAP simultaneously to validate results match before cutting over.

### Duration
- Minimum: 3 complete pay periods across all payroll areas
- Recommended: Include at least one month-end close and one quarter-end

### Process
```
1. Run regular payroll in LEGACY system (production)
2. Run same-period payroll in SAP (simulation/test)
3. Extract results from both systems
4. Compare employee-by-employee:
   - Gross pay
   - Each deduction
   - Each tax withholding
   - Net pay
5. Investigate and resolve ALL differences
6. Document resolution for audit trail
7. Repeat for next period
```

### Tolerance Thresholds
| Element | Tolerance | Action if Exceeded |
|---------|-----------|-------------------|
| Gross Pay | +/- $0.01 | Investigate immediately |
| Net Pay | +/- $0.05 | Investigate; may be rounding |
| Federal Tax | Exact match | Must resolve |
| State Tax | +/- $0.01 | Investigate; may be rounding |
| FICA | Exact match | Must resolve (wage base sensitive) |
| Deductions | Exact match | Must resolve |

### Comparison Report
Custom ABAP report comparing legacy extract vs. SAP payroll result tables:
- Input: Legacy CSV + SAP RT/CRT cluster data
- Output: Variance report by employee with difference amounts
- Highlight: Employees outside tolerance threshold
- Summary: Total match rate (target: 98%+ within tolerance)

## Go/No-Go Criteria

### Must-Pass Criteria
1. 98% of employees within tolerance for 3 consecutive periods
2. All tax differences resolved and documented
3. All interfaces tested end-to-end (bank, tax filing, 401k, benefits)
4. PCC alerts reviewed and resolution procedures documented
5. Pay slip layout approved by HR
6. GL posting reconciliation balanced
7. Year-to-date balances verified for all employees
8. Garnishment calculations validated against court orders
9. Off-cycle payroll tested (termination, correction, bonus)
10. Disaster recovery / rollback plan documented

### Sign-Off Required From
- Payroll Manager
- HR VP
- CFO / Finance Controller
- SAP Project Manager
- IT / Basis Team Lead

## Cutover Sequence

### Pre-Cutover (T-2 weeks)
1. Final data refresh from legacy to SAP QA
2. Full regression test of all payroll areas
3. Interface connectivity test (all systems)
4. User acceptance testing (UAT) sign-off

### Cutover Weekend (T-0)
```
Day 1 (Friday):
  1. Final payroll run in legacy system
  2. Freeze legacy system (no more changes)
  3. Extract final master data delta

Day 2 (Saturday):
  4. Load delta data to SAP Production
  5. Load final YTD balances (IT0559)
  6. Validate employee count and key totals

Day 3 (Sunday):
  7. Run payroll simulation in SAP Production
  8. Spot-check 50+ employees across all payroll areas
  9. Go/No-Go decision by 6:00 PM
  10. If GO: SAP Production is live for payroll
  11. If NO-GO: Activate rollback plan (continue legacy)
```

### Post-Cutover (T+1 to T+4 weeks)
1. First live SAP payroll run (hypercare support)
2. Employee-by-employee verification of first paycheck
3. Monitor PCC alerts closely
4. Verify bank transfer / ACH processing
5. Verify FI posting and GL reconciliation
6. Collect and address employee pay slip questions
7. Weekly status meetings during hypercare
