# FI Posting & Symbolic Account Reference

## Posting Architecture

### Program: RPCIPTU0 (Posting to Accounting)
- Posts payroll results from HR cluster (PCL2) to SAP FI/CO
- Creates FI documents with posting key 40 (debit) / 50 (credit)
- Document type: PY (payroll posting)
- Cost allocation via cost center from IT0001 (Organizational Assignment)

### Posting Flow
```
Payroll Results (RT/CRT tables)
    ↓
Symbolic Account Mapping (V_T52EL)
    ↓
Account Determination (V_T52E4)
    ↓
GL Account Assignment + Cost Object
    ↓
FI Document Creation (RPCIPTU0)
    ↓
GL Posting
```

## Symbolic Account Design

### Standard Symbolic Account Pattern
| Category | SA Range | Description | GL Type |
|----------|----------|-------------|---------|
| Expenses | SA01-SA09 | Compensation expense accounts | P&L Debit |
| ER Taxes | SA10-SA19 | Employer tax expense accounts | P&L Debit |
| ER Benefits | SA12 | Employer benefit expense | P&L Debit |
| Tax Liabilities | SA20-SA29 | Tax withholding payable | BS Credit |
| Benefit Liabilities | SA30-SA39 | Benefit deduction payable | BS Credit |
| Net Pay | SA40 | Net pay clearing | BS Credit |
| Bank | SA41 | Bank disbursement clearing | BS Debit (offset) |

### Detailed Symbolic Account Mapping
| SA | Description | GL Account | D/C | Wage Types |
|----|-------------|------------|-----|------------|
| SA01 | Salaries & Wages | 6100xx | D | 1000,1010,1020,1030,1060-1090 |
| SA02 | Shift & Premium | 6101xx | D | 1040,1041,1050 |
| SA03 | Bonus & Commission | 6102xx | D | 1100,1110,1120,1170 |
| SA04 | Other Compensation | 6103xx | D | 1130,1140,1160 |
| SA10 | ER FICA | 6200xx | D | /109,/110 |
| SA11 | ER FUTA/SUTA | 6201xx | D | /111,/112 |
| SA12 | ER Benefits | 6300xx | D | 3020-3080 |
| SA20 | Federal Tax Payable | 2100xx | C | /101 |
| SA21 | State/Local Tax | 2101xx | C | /104-/107 |
| SA22 | FICA Payable | 2102xx | C | /102,/103,/109,/110 |
| SA23 | FUTA/SUTA Payable | 2103xx | C | /111,/112 |
| SA30 | Benefit Ded Payable | 2200xx | C | 2060-2091 |
| SA31 | 401(k) Payable | 2201xx | C | 2070-2072,3050 |
| SA32 | Garnishment Payable | 2300xx | C | Garn WTs |
| SA40 | Net Pay Clearing | 2400xx | C | Net pay |
| SA41 | Bank Clearing | 1100xx | D | ACH |

## Configuration Tables

### V_T52EL - Symbolic Accounts
- Maps wage types to symbolic accounts
- Key: wage type + evaluation class
- IMG: Payroll > Payroll: USA > Reporting > Posting to FI > Symbolic Accounts

### V_T52E4 - Account Determination
- Maps symbolic accounts to GL accounts
- Key: symbolic account + company code + personnel area (optional)
- Allows different GL accounts by PA for multi-entity setups
- IMG: Payroll > Posting to FI > Define Account Determination

### V_T52EK - Posting Variants
- Controls posting behavior (document splitting, date rules)
- IMG: Payroll > Posting to FI > Define Posting Variants

## Reconciliation

### Program: RPCPRRU0
- Compares HR payroll results totals to FI posted totals
- Run monthly as part of period-end close
- Identifies: missing postings, amount mismatches, timing differences

### Reconciliation Checklist
1. Run RPCPRRU0 for the period
2. Compare total gross pay (HR) vs. salary expense postings (FI)
3. Compare total deductions (HR) vs. liability account credits (FI)
4. Compare net pay (HR) vs. bank clearing (FI)
5. Investigate any differences
6. Common causes: retro adjustments, off-cycle runs, manual journal entries

## Cost Allocation
- Primary cost object: Cost center from IT0001 (position → org unit → cost center)
- Secondary: Internal order, WBS element (if project-based)
- Cost center split: Can split posting across multiple cost centers via IT0027
- Profit center: Derived from cost center assignment in CO

## Bank Transfer Integration
- Program: RFFOUS_T (US ACH file generation)
- Format: NACHA CCD+ (corporate) / PPD+ (employee)
- House bank configuration: T012 (bank master), T012K (account)
- Payment method: T = ACH Transfer, C = Check
- Employee bank details: IT0009 (up to 3 account splits)
- Pre-note period: 10 days for new/changed accounts

## Posting Variant Configuration (V_T52EK)

### Key Settings
| Setting | Description | Options |
|---------|-------------|---------|
| Posting date | Which date to use for FI document | Payroll end date / Pay date / Custom |
| Document splitting | Split by cost center | Y/N |
| Summarization | Summarize by wage type or post individual | Per WT / Summarized |
| Negative posting | How to handle negative amounts | Reverse D/C / Statistical |
| Off-cycle posting | Separate document type for off-cycle | PY / ZP (custom) |

### Multi-Entity Posting
For companies with multiple company codes or personnel areas:
- V_T52E4 supports GL account determination by: Symbolic Account + Company Code + Personnel Area
- Different GL accounts per PA allow plant-specific cost tracking
- Different company codes require separate posting runs

## Cost Distribution (IT0027)

When an employee's costs split across multiple cost centers:
| Field | Purpose |
|-------|---------|
| Cost Center | Target cost object |
| Percentage | % allocation |
| WBS Element | Project cost allocation (if project-based) |
| Internal Order | Order-based allocation |
| Validity dates | Begin/end date for split |

Use IT0027 for:
- Shared employees across departments
- Project-based cost allocation
- Temporary reassignments

## Period-End Close Checklist
1. Run payroll for all areas in the period
2. Post to FI (RPCIPTU0)
3. Run reconciliation (RPCPRRU0)
4. Investigate and resolve any differences
5. Post manual adjustments if needed
6. Close payroll period (PU03)
7. Run cost center reports (S_AHR_61016380)
8. Verify FUTA/SUTA liability postings
9. Archive payroll documents
