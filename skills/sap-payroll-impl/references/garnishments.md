# Garnishment Processing Reference

## SAP Garnishment Infotypes

### IT0194 - Garnishment Order
- One record per garnishment order per employee
- Key fields: garnishment type, payee, court/agency, case number, order amount, start/end dates
- Subtypes correspond to garnishment types (CS, FL, SL, ED, CG, BK)

### IT0195 - Garnishment Adjustment / Document
- Supporting details for garnishment orders
- Fee amounts, arrears tracking, adjustment amounts
- Links to IT0194 via garnishment order number

## CCPA Priority Rules (Federal)

### Standard Priority Order
| Priority | Type | Code | CCPA Max % of Disposable |
|----------|------|------|--------------------------|
| 1 | Child Support / Alimony | CS | 50-65% |
| 2 | Federal Tax Levy (IRS) | FL | Per IRS Pub 1494 |
| 3 | State Tax Levy | SL | Per state rules |
| 4 | Federal Student Loan (DOE) | ED | 15% |
| 5 | Creditor Garnishment | CG | 25% or 30x min wage |
| 6 | Bankruptcy (Chapter 13) | BK | Per court plan |

### Child Support Details
- 50% if supporting another spouse/child, no arrears
- 55% if supporting another spouse/child, with arrears >12 weeks
- 60% if NOT supporting another spouse/child, no arrears
- 65% if NOT supporting another spouse/child, with arrears >12 weeks
- State orders may specify different amounts within CCPA limits

### Federal Tax Levy (IRS)
- Not subject to CCPA percentage limits
- Exempt amount per IRS Publication 1494 (updated annually)
- Based on filing status + number of exemptions claimed on Statement of Exemptions (Form 668-W)
- Takes priority over creditor garnishments but after child support

### Creditor Garnishment
- Lesser of: 25% of disposable earnings OR amount by which weekly disposable exceeds 30x federal minimum wage
- Federal minimum wage: $7.25/hr → 30x = $217.50/week
- State limits may be more protective (lower % or higher exempt amounts)

## Disposable Income Calculation

### Formula
```
Gross Pay (all earnings)
  - Federal Income Tax withheld
  - State Income Tax withheld
  - Local Income Tax withheld
  - FICA (Social Security + Medicare) withheld
  - Mandatory state deductions (SDI, SUI EE share where applicable)
  - Court-ordered health insurance (if applicable)
= Disposable Income
```

### Pre-Tax Deductions
- Health insurance premiums (Section 125) — generally subtracted from disposable
- 401(k) pre-tax contributions — treatment varies by state
- FSA — generally subtracted from disposable

## State-Specific Variations

### California
- Maximum garnishment: 25% of disposable or amount exceeding 40x CA minimum wage
- CA minimum wage is higher than federal → more protective
- Head of household exemption: lower garnishment percentage
- Earnings withholding order (EWO) for state tax levies

### New York
- 10% of gross or 25% of disposable, whichever is less (for consumer debt)
- Higher protections: minimum wage x 30 exempt amount uses NY minimum (not federal)
- Child support: per court order within CCPA limits
- Income execution for tax debts: up to 10% of gross

### Illinois
- Maximum: 15% of gross or amount exceeding 45x federal minimum wage
- Administrative wage deduction for child support
- State tax levy: per IL Department of Revenue order

### Florida
- Head of family exemption: 100% of disposable earnings exempt if providing >50% support
- Must claim exemption; not automatic
- If not head of family: standard CCPA limits apply

### Texas
- Very limited garnishment allowed (child support, student loans, tax levies, spousal maintenance)
- General creditor garnishment NOT permitted under Texas law
- Child support enforcement through Attorney General

## Multi-Garnishment Processing

### Proration Rules
When combined garnishments exceed CCPA limits:
1. Process in priority order
2. Higher-priority garnishments satisfied first
3. Lower-priority garnishments get remaining capacity
4. If same priority, prorate proportionally by order amount

### SAP Processing
- Function UGARN in schema U000 handles garnishment calculation
- Processes after tax calculation (needs tax amounts for disposable income)
- SAP table V_T5UGS defines garnishment types and priorities
- SAP table V_T5UGT defines state-specific limits and rules

## Configuration Tables
| Table | Purpose |
|-------|---------|
| V_T5UGS | Garnishment type definitions and priority |
| V_T5UGT | State-specific garnishment rules and limits |
| V_T5UGA | Garnishment adjustment types |
| V_T5UGP | Garnishment payee information |
| T5UG1 | Garnishment calculation rules |

## Remittance
- Third-party payee payments via regular or off-cycle payroll
- Check or EFT to court/agency/payee
- Tracking of remittance dates for compliance
- State-specific remittance deadlines (typically within 7 days of withholding)

## Additional State-Specific Rules

### Pennsylvania
- Consumer debt: Generally NO wage garnishment for consumer debt
- Only child support, tax levies, and student loans
- Very employee-protective state

### Massachusetts
- Minimum exemption: $750/week (adjusted annually)
- Consumer debt: follows CCPA limits

### New Jersey
- 10% of gross if earnings ≤250% poverty; 25% of disposable otherwise
- Very protective for low-income earners

### Oregon
- Exempt amount updates annually (75% of min wage × 40)

### Ohio
- Municipal garnishment rules vary
- Standard CCPA for consumer debt

### Washington
- Head of family: 75% of disposable exempt
- Standard CCPA limits otherwise

## Disposable Income Calculation (Detailed)

### Items ALWAYS Subtracted from Gross
1. Federal income tax withheld
2. State income tax withheld
3. Local income tax withheld
4. Social Security (OASDI) - employee share
5. Medicare - employee share
6. Mandatory state disability insurance (CA SDI, NJ TDI, NY DBL, HI TDI)
7. Mandatory state PFML contributions (WA, MA, CT, CO, OR)

### Variable Treatment Items
| Item | Federal Default | Notes |
|------|----------------|-------|
| Health insurance (§125) | Generally subtracted | Some states exclude |
| 401(k) pre-tax | Generally NOT subtracted | CA subtracts; varies |
| Union dues | Generally NOT subtracted | Some states subtract |
| FSA contributions | Generally subtracted | Varies |

**SAP**: Configure via Processing Class 20 on each wage type. PC20=01 = included in disposable; PC20=02 = excluded.

## Garnishment Fee Handling
| Approach | Description |
|----------|------------|
| Employer-paid | Most common — employer absorbs |
| Employee-paid | Some states allow (GA $25/mo, IN $12/payment) |
| State-mandated | State sets fee amount |
