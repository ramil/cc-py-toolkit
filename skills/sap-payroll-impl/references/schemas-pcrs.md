# Schema & PCR Reference

## US Payroll Schema Architecture

### Schema Hierarchy (US Payroll)
```
U000 (US Payroll Driver)
  ├── UT00 (Tax Initialization)
  ├── U001 (Gross Calculation)
  │     ├── Basic pay processing (IT0008)
  │     ├── Recurring deductions/payments (IT0014/0015)
  │     └── Time wage types (from RPTIME00)
  ├── UTAX (Tax Calculation - BSI)
  │     ├── Federal tax (FITW, FICA, FUTA)
  │     ├── State tax (SIT, SUI, SDI)
  │     └── Local tax
  ├── U0G0 (Garnishment Processing - UGARN)
  ├── UNET (Net Calculation)
  │     ├── Pre-tax deduction subtraction
  │     ├── Tax subtraction
  │     ├── Post-tax deduction subtraction
  │     └── Net pay determination
  └── UEND (End of Payroll - Cumulations)
        ├── YTD/QTD/MTD accumulations
        ├── Evaluation class cumulation
        └── Retroactive difference calculation
```

### Schema Customization Approach
1. **Never modify SAP standard schemas directly**
2. Copy U000 to ZU00 (or customer namespace)
3. Copy TM04 to ZTM4 for time evaluation customization
4. Copy UEND to ZUEN for custom cumulation rules
5. Add custom functions/PCR calls within copied schemas
6. Transport via PE01 (schema editor)

## Key Schema Functions

### Earnings Functions
| Function | Purpose |
|----------|---------|
| UVAC | Vacation/absence valuation |
| UBEN | Benefits calculation |
| UPAY | Basic pay processing |
| UADD | Additional payments (IT0015) |
| UREC | Recurring deductions (IT0014) |

### Tax Functions
| Function | Purpose |
|----------|---------|
| UTXF | Federal tax calculation (BSI) |
| UTXS | State tax calculation (BSI) |
| UTXL | Local tax calculation (BSI) |
| UFIC | FICA calculation (BSI) |
| UFUT | FUTA calculation (BSI) |

### Other Functions
| Function | Purpose |
|----------|---------|
| UGARN | Garnishment processing |
| UNET | Net pay calculation |
| UBNK | Bank transfer preparation |
| UCUM | Cumulation (YTD/QTD/MTD) |
| URRP | Retroactive processing |

## Common Custom PCRs

### PCR: California Daily Overtime
**Purpose**: CA requires daily OT (>8 hrs = 1.5x, >12 hrs = 2.0x) in addition to federal weekly OT
**Triggered by**: Time evaluation schema (ZTM4)
**Applicable to**: Hourly employees in CA personnel areas
**Logic**:
```
IF work state = CA AND EE subgroup IN (02, 04)
  IF daily hours > 12
    Hours 8.01-12.00 → WT 1020 (1.5x)
    Hours > 12.00 → WT 1030 (2.0x)
  ELSEIF daily hours > 8
    Hours > 8.00 → WT 1020 (1.5x)
  ENDIF
  // 7th consecutive day rules also apply
ENDIF
```

### PCR: 401(k) Employer Match
**Purpose**: Calculate tiered employer match
**Common formulas**:
- Simple: 100% match up to X% of salary
- Tiered: 100% on first 3% + 50% on next 3% = max 4.5% ER
- Safe Harbor: 100% match up to 4% (or 3% non-elective)
**Logic**:
```
EE contribution % = WT 2070 amount / eligible compensation
IF EE% <= 3%
  ER match = EE contribution amount x 100%
ELSEIF EE% <= 6%
  ER match = (3% x comp x 100%) + ((EE% - 3%) x comp x 50%)
ELSE
  ER match = (3% x comp x 100%) + (3% x comp x 50%)  // cap at 4.5%
ENDIF
Store in WT 3050
```

### PCR: Imputed Income (Group-Term Life > $50K)
**Purpose**: Calculate taxable imputed income per IRS Table I for group-term life coverage exceeding $50,000
**Logic**:
```
Coverage amount = annual salary x multiplier (from IT0168)
IF coverage > $50,000
  Taxable portion = (coverage - $50,000) / $1,000 x IRS Table I rate x months
  IRS Table I rates (monthly cost per $1,000):
    Under 25: $0.05    25-29: $0.06    30-34: $0.08
    35-39: $0.09       40-44: $0.10    45-49: $0.15
    50-54: $0.23       55-59: $0.43    60-64: $0.66
    65-69: $1.27       70+: $2.06
  Add imputed income as taxable earnings
ENDIF
```

### PCR: Shift Differential Assignment
**Purpose**: Assign shift premium wage types based on work schedule or IT2003
**Logic**:
```
IF shift from IT2003 or work schedule = 2nd shift (3pm-11pm)
  Generate WT 1040 for hours x $X.XX/hr
ELSEIF shift = 3rd shift (11pm-7am)
  Generate WT 1041 for hours x $X.XX/hr
ENDIF
```

### PCR: PTO Accrual by Tenure
**Purpose**: Variable PTO accrual based on years of service
**Common bands**:
```
Years of Service    Annual PTO Days    Accrual per Pay Period
0-2 years           15 days            Based on pay frequency
3-5 years           18 days
6-10 years          20 days
11+ years           25 days
```

### PCR: Supplemental Tax Routing
**Purpose**: Route supplemental earnings through flat-rate tax method
**Logic**:
```
IF wage type IN (1100, 1110, 1120, 1130, 1140, 1170)
  Set processing class 10 = 02 (supplemental)
  // BSI applies 22% federal flat rate
  // State supplemental rates where applicable
ENDIF
```

## Time Evaluation Schema (TM04/ZTM4)

### Key Time Evaluation Functions
| Function | Purpose |
|----------|---------|
| P2001 | Read absences |
| P2002 | Read attendances |
| P2003 | Read substitutions |
| POT | Overtime determination |
| PTIP | Time type processing |
| GWT | Generate time wage types for payroll |

### Overtime Calculation Methods
- **Federal (FLSA)**: Weekly >40 hours = 1.5x
- **California**: Daily >8 = 1.5x, Daily >12 = 2.0x, 7th consecutive day
- **Weighted Average**: Multi-rate OT calculation for employees with multiple pay rates
- **SAP handles** FLSA weekly OT natively; daily OT requires custom PCR

## Transaction Codes
| TCode | Description |
|-------|-------------|
| PE01 | Schema Editor (view/edit schemas) |
| PE02 | PCR Editor (view/edit calculation rules) |
| PE03 | Feature Editor (ABKRS, LGMST, etc.) |
| PE04 | Create function (for schemas) |
| PC00_M10_CALC | Run US Payroll |
| PC00_M10_CALC_SIMU | Payroll Simulation |
| PC_PAYRESULT | Display Payroll Results (RT/CRT) |
| PT60 | Time Evaluation |
| PU03 | Change Payroll Status (control record) |
