# Benefits Configuration Reference

## SAP Benefits Framework

### Key Infotypes
| IT | Name | Purpose |
|----|------|---------|
| 0167 | Health Plan | Medical/dental/vision enrollment |
| 0168 | Insurance Plan | Life, AD&D, STD, LTD coverage amounts |
| 0169 | Savings Plan | 401(k), Roth, after-tax savings elections |
| 0170 | Flexible Spending Account | FSA, HSA, DCFSA elections |
| 0171 | General Benefits Info | COBRA status, ACA tracking |
| 0236 | Credit Plan | Flex benefits credits (if cafeteria plan) |

### SAP Benefits Tables
| Table | Purpose |
|-------|---------|
| T5UBP | Benefit plan master |
| T5UB1 | Benefit plan options (coverage tiers) |
| T74FC | Benefit area configuration |
| V_T74FD | Plan-to-payroll integration (EE deduction WT + ER contribution WT) |
| T5UBA | Benefit eligibility rules |
| T5UBV | Benefit vesting schedules |
| T5UBC | Benefit cost tables (premium rates by tier) |

### IMG Path
`Personnel Management > Benefits > Plans`

## Standard Benefit Plan Types

### Health & Welfare Plans

#### Medical Insurance
| Field | Typical Values |
|-------|---------------|
| Plan Type | MEDI |
| Coverage Tiers | EE Only, EE+Spouse, EE+Child(ren), Family |
| Section | IRC §125 (pre-tax via cafeteria plan) |
| IT Source | IT0167 |
| EE Deduction WT | 2060 |
| ER Contribution WT | 3020 |
| Eligibility | Full-time active (≥30 hrs/week for ACA) |
| Waiting Period | 1st of month after 30/60/90 days |
| Enrollment Events | New hire, open enrollment, qualifying life event |

#### Dental Insurance
| Field | Typical Values |
|-------|---------------|
| Plan Type | DENT |
| Coverage Tiers | EE Only, EE+Spouse, EE+Child(ren), Family |
| Section | IRC §125 |
| EE Deduction WT | 2061 |
| ER Contribution WT | 3030 |

#### Vision Insurance
| Field | Typical Values |
|-------|---------------|
| Plan Type | VISN |
| Coverage Tiers | EE Only, EE+Family |
| Section | IRC §125 |
| EE Deduction WT | 2062 |
| ER Contribution WT | 3040 |

### Retirement Plans

#### 401(k) Pre-Tax
| Field | Typical Values |
|-------|---------------|
| Plan Type | 401K |
| Section | IRC §401(k) |
| IT Source | IT0169 |
| EE Deduction WT | 2070 |
| ER Match WT | 3050 |
| Election Type | % of eligible compensation or flat $ |
| IRS Limit (2026) | $23,500 (projected) |
| Catch-Up (50+) | $7,500 additional |
| Super Catch-Up (60-63) | $11,250 additional (SECURE 2.0, effective 2025) |
| Auto-Enroll | SECURE 2.0 requires for new plans (3-10% default) |

#### Common Match Formulas
| Pattern | Formula | Max ER Cost |
|---------|---------|-------------|
| Simple 100% | 100% match up to X% of comp | X% of payroll |
| Tiered | 100% on first 3% + 50% on next 3% | 4.5% of payroll |
| Safe Harbor Basic | 100% match up to 4% of comp | 4% of payroll |
| Safe Harbor Non-Elective | 3% of comp to all eligible (no EE contrib needed) | 3% of payroll |
| Graded | 50% match up to 6% of comp | 3% of payroll |

#### 401(k) Roth
| Field | Typical Values |
|-------|---------------|
| Plan Type | ROTH |
| Section | IRC §402A |
| EE Deduction WT | 2071 |
| Tax Treatment | Post-tax (no pre-tax deduction) |
| Combined Limit | Shared with pre-tax 401(k) ($23,500) |

#### 401(k) Catch-Up
| Field | Typical Values |
|-------|---------------|
| Plan Type | 401C |
| EE Deduction WT | 2072 |
| Eligibility | Age 50+ by end of plan year |

### Flexible Spending Accounts

#### FSA Medical (Healthcare)
| Field | Typical Values |
|-------|---------------|
| Plan Type | FSAM |
| Section | IRC §125 |
| IT Source | IT0170 |
| EE Deduction WT | 2080 |
| Annual Limit (2026) | $3,300 (projected) |
| Carryover | Up to $640 (2026 projected) or grace period |
| Use-It-or-Lose-It | Yes (unless carryover/grace elected) |

#### FSA Dependent Care (DCFSA)
| Field | Typical Values |
|-------|---------------|
| Plan Type | FSAD |
| Section | IRC §129 |
| EE Deduction WT | 2081 |
| Annual Limit | $5,000 ($2,500 if MFS) |

#### Health Savings Account (HSA)
| Field | Typical Values |
|-------|---------------|
| Plan Type | HSA |
| Section | IRC §223 |
| EE Deduction WT | 2082 (custom) |
| ER Contribution WT | 3055 (custom) |
| Eligibility | Must be enrolled in HDHP |
| Annual Limit (Self, 2026) | ~$4,300 (projected) |
| Annual Limit (Family, 2026) | ~$8,550 (projected) |
| Catch-Up (55+) | $1,000 additional |
| Portability | Employee-owned, fully vested immediately |

### Insurance Plans

#### Group-Term Life (Basic)
| Field | Typical Values |
|-------|---------------|
| Plan Type | LIFE |
| IT Source | IT0168 |
| Coverage | 1x or 2x annual salary |
| ER Contribution WT | 3060 |
| Non-Taxable Threshold | $50,000 (IRS Table I imputed income above this) |
| Imputed Income WT | Custom earnings WT (taxable) |

#### Supplemental Life (Voluntary)
| Field | Typical Values |
|-------|---------------|
| Plan Type | SLFE |
| EE Deduction WT | 2090 |
| Coverage | 1x-5x salary in increments |
| Tax Treatment | Post-tax |
| EOI Required | Typically above 3x salary |

#### AD&D (Accidental Death & Dismemberment)
| Field | Typical Values |
|-------|---------------|
| Plan Type | ADDS |
| EE Deduction WT | 2091 |
| Coverage | Matches group life or voluntary selection |

#### Short-Term Disability (STD)
| Field | Typical Values |
|-------|---------------|
| Plan Type | STD |
| ER Contribution WT | 3070 |
| Benefit | 60-66.7% of base salary |
| Duration | Up to 26 weeks |
| Elimination Period | 7-14 days |
| State STD/TDI | CA SDI, NJ TDI, NY DBL, HI TDI, RI TDI (employer may opt private) |

#### Long-Term Disability (LTD)
| Field | Typical Values |
|-------|---------------|
| Plan Type | LTD |
| ER Contribution WT | 3080 |
| Benefit | 60% of base salary |
| Duration | To age 65 or SSNRA |
| Elimination Period | 90-180 days |

### Union-Specific Benefits

#### H&W (Health & Welfare) Fund
| Field | Typical Values |
|-------|---------------|
| Plan Type | UNHW (custom) |
| ER Contribution WT | 3090 (custom) |
| Calculation | Fixed $/hour worked (per CBA) |
| Remittance | Monthly to union trust fund |
| Vesting | Immediate (per CBA) |

#### Union Pension (Defined Benefit)
| Field | Typical Values |
|-------|---------------|
| Plan Type | UNPN (custom) |
| ER Contribution WT | 3095 (custom) |
| Calculation | Fixed $/hour worked or % of gross (per CBA) |
| Vesting | Per ERISA (typically 5-year cliff or 7-year graded) |
| Remittance | Monthly to pension trust fund |

#### Union Dues
| Field | Typical Values |
|-------|---------------|
| Deduction Type | Post-tax |
| EE Deduction WT | 2130 |
| Calculation | Fixed $/month or % of gross (per CBA) |
| Authorization | Signed dues checkoff card |

## Eligibility Rules

### Standard Patterns
| Rule | Description | Typical Use |
|------|------------|-------------|
| All Active FT | All active employees ≥30 hrs/week | Health plans (ACA) |
| All Active | All active employees regardless of hours | 401k, basic life |
| After Waiting | Eligible after X days of service | Health plans (30/60/90 day) |
| Salaried Only | EE Subgroup 01, 03 only | Executive plans |
| Union Only | EE Subgroup with union flag | Union H&W, pension |
| Non-Union Only | EE Subgroup without union flag | 401k, FSA, HSA |
| Age-Based | Age 50+ (catch-up), Age 21+ (401k) | Retirement plan extras |

### ACA Full-Time Determination
- Standard: ≥30 hours/week average
- Measurement period: Look-back (12 months), stability period (12 months)
- Variable-hour employees: Track via IT0171 or external ACA system
- 1095-C reporting: Annual, due March

## IRS Annual Limits (Update Every January)

| Limit | 2025 | 2026 (Projected) |
|-------|------|-------------------|
| 401(k) Deferral | $23,500 | $23,500 |
| 401(k) Catch-Up (50+) | $7,500 | $7,500 |
| 401(k) Super Catch-Up (60-63) | $11,250 | $11,250 |
| Total 415 Limit (EE+ER) | $70,000 | $70,000 |
| SS Wage Base | $168,600 | $174,900 |
| HCE Compensation | $155,000 | $160,000 |
| FSA Medical | $3,200 | $3,300 |
| FSA Carryover | $640 | $640 |
| FSA Dep Care | $5,000 | $5,000 |
| HSA Self | $4,150 | $4,300 |
| HSA Family | $8,300 | $8,550 |
| HSA Catch-Up (55+) | $1,000 | $1,000 |
| Group Life Non-Taxable | $50,000 | $50,000 |
| Tuition Non-Taxable | $5,250 | $5,250 |
| Transit/Parking Pre-Tax | $315/mo | $325/mo |
