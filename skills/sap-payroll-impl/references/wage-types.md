# Wage Type Reference

## Wage Type Architecture

### Naming Ranges (US Payroll - Molga 10)
| Range | Category | Source |
|-------|----------|--------|
| /001-/099 | SAP internal technical WTs | System |
| /100-/199 | Tax wage types (BSI) | System/BSI |
| /200-/299 | Net calculation WTs | System |
| /300-/399 | Cumulation WTs | System |
| /400-/499 | Garnishment WTs | System |
| /500-/599 | Retroactive WTs | System |
| 1000-1999 | Custom earnings | Model M-series copy |
| 2000-2999 | Custom deductions | Model D-series copy |
| 3000-3999 | Custom ER contributions | Model E-series copy |

### Creating Custom Wage Types
1. Go to SM30 > V_T511 (or SPRO path)
2. Copy from appropriate model wage type
3. Assign processing classes (V_T52D0)
4. Assign evaluation classes (V_T52D1)
5. Set permissibility per EE Subgroup (V_T511)
6. Configure cumulation (V_T54C1)
7. Set up symbolic account for FI posting (V_T52EL)

## Standard Earnings Wage Types

### Regular Earnings
| WT | Description | Model | IT Source | Amount Type |
|----|-------------|-------|-----------|-------------|
| 1000 | Base Salary | M100 | IT0008 | Monthly/Annual |
| 1010 | Regular Hours | M110 | IT2001/2002 | Hours x Rate |
| 1020 | Overtime 1.5x | M120 | IT2002/RPTIME | Hours x Rate x 1.5 |
| 1030 | Double Time 2.0x | M130 | IT2002/RPTIME | Hours x Rate x 2.0 |
| 1040 | Shift Diff - 2nd | M140 | IT2003/RPTIME | $/hr add-on |
| 1041 | Shift Diff - 3rd | M140 | IT2003/RPTIME | $/hr add-on |
| 1050 | Holiday Premium | M150 | RPTIME | Hours x Rate x multiplier |

### Absence Earnings
| WT | Description | Model | IT Source | Valuation |
|----|-------------|-------|-----------|-----------|
| 1060 | PTO / Vacation | M160 | IT2001 | Regular rate |
| 1070 | Sick Pay | M170 | IT2001 | Regular rate |
| 1080 | Bereavement | M180 | IT2001 | Regular rate |
| 1090 | Jury Duty | M190 | IT2001 | Regular rate |
| 1095 | FMLA (tracking) | M195 | IT2001 | Unpaid |

### Supplemental Earnings
| WT | Description | Model | IT Source | Tax Treatment |
|----|-------------|-------|-----------|---------------|
| 1100 | Annual Bonus | M210 | IT0015 | Supplemental (flat 22% fed) |
| 1110 | Spot Bonus | M210 | IT0015 | Supplemental |
| 1120 | Commission | M220 | IT0015 | Supplemental |
| 1130 | Relocation | M230 | IT0015 | Supplemental |
| 1140 | Severance | M240 | IT0015 | Supplemental |
| 1150 | Retro Pay Adj | /551 | System | Regular (retro) |
| 1160 | Tuition Reimb | M260 | IT0015 | Non-taxable < $5,250 |
| 1170 | Referral Bonus | M210 | IT0015 | Supplemental |

## Standard Deduction Wage Types

### Statutory Deductions (BSI-Generated)
| WT | Description | Calculation |
|----|-------------|-------------|
| /101 | Federal Income Tax | BSI FITW based on IT0210 W-4 |
| /102 | Social Security EE | 6.2% up to wage base |
| /103 | Medicare EE | 1.45% + 0.9% Additional > $200K |
| /104 | State Income Tax | BSI per state rules |
| /105 | Local / City Tax | BSI per local rules |
| /106 | CA SDI | California SDI rate |
| /107 | NY SDI / PFL | New York SDI + Paid Family Leave |

### Voluntary Deductions
| WT | Description | Model | Pre/Post Tax | Section |
|----|-------------|-------|-------------|---------|
| 2060 | Medical EE | D100 | Pre-tax | Sec 125 |
| 2061 | Dental EE | D110 | Pre-tax | Sec 125 |
| 2062 | Vision EE | D120 | Pre-tax | Sec 125 |
| 2070 | 401(k) Pre-Tax | D200 | Pre-tax | Sec 401(k) |
| 2071 | 401(k) Roth | D210 | Post-tax | Roth |
| 2072 | 401(k) Catch-Up | D220 | Pre-tax | Age 50+ |
| 2080 | FSA Medical | D300 | Pre-tax | Sec 125 |
| 2081 | FSA Dep Care | D310 | Pre-tax | Sec 129 |
| 2090 | Supplemental Life | D400 | Post-tax | N/A |
| 2091 | AD&D | D410 | Post-tax | N/A |
| 2130 | Union Dues | D500 | Post-tax | N/A |

## Employer Contribution Wage Types
| WT | Description | Model | Calculation |
|----|-------------|-------|-------------|
| /109 | ER FICA-SS | System | 6.2% to wage base |
| /110 | ER FICA-Med | System | 1.45% all wages |
| /111 | ER FUTA | System | 0.6% effective to $7,000 |
| /112 | ER SUTA | System | Per state experience rate |
| 3020 | ER Medical | E100 | Flat per enrollment tier |
| 3030 | ER Dental | E110 | Flat per enrollment tier |
| 3040 | ER Vision | E120 | Flat per enrollment tier |
| 3050 | ER 401(k) Match | E200 | Formula: match % of EE contrib |
| 3060 | ER Group Life | E300 | 1x salary carrier rate |
| 3070 | ER STD | E310 | Carrier rate |
| 3080 | ER LTD | E320 | Carrier rate |

## Processing Classes (V_T52D0)

### Key Processing Classes for US Payroll
| PC | Name | Description | Common Values |
|----|------|-------------|---------------|
| 01 | EE Grouping | Controls permissibility by EE subgroup | 01-04 for active subgroups |
| 02 | Time Processing | How the WT interacts with time evaluation | 1=time-based, 2=lump, 3=OT, 5=absence |
| 03 | Cumulation | Which cumulation WT to feed | Maps to /3xx cumulation WTs |
| 10 | Tax Treatment | Federal/state tax method | 01=regular, 02=supplemental, 03=non-taxable |
| 20 | Garnishment | Include in disposable income calc | 01=include, 02=exclude |
| 30 | Benefits Base | Include in benefits-eligible compensation | 01=include, 02=exclude |
| 40 | 401(k) Base | Include in 401(k)-eligible compensation | 01=include, 02=exclude |
| 71 | FI Posting | Symbolic account for GL posting | SA01-SA41 etc. |

## Evaluation Classes (V_T52D1)
| EC | Name | Purpose |
|----|------|---------|
| 01 | Earnings Type | 01=regular, 02=supplemental, 03=non-taxable |
| 02 | Deduction Type | 01=pre-tax, 02=post-tax, 03=statutory |
| 10 | W-2 Box | Maps to W-2 reporting box |
| 20 | Workers Comp | WC class code assignment |

## Additional Industry-Specific Wage Types

### Healthcare
| WT | Description | Model | Calculation |
|----|-------------|-------|-------------|
| 1180 | On-Call Pay | M140 | Fixed $/hr while on standby |
| 1181 | Callback Pay | M150 | Minimum 2-4 hrs at 1.5x |
| 1182 | Charge Nurse Premium | M140 | $/hr add-on |
| 1183 | Weekend Differential | M140 | $/hr add-on or % |
| 1184 | PRN/Per Diem Rate | M110 | Special daily rate |
| 1185 | Certification Premium | M140 | $/hr for specialized certs |

### Manufacturing / Construction
| WT | Description | Model | Calculation |
|----|-------------|-------|-------------|
| 1190 | Prevailing Wage Base | M110 | Per Davis-Bacon determination |
| 1191 | Prevailing Wage Fringe | M140 | Fringe portion of PW rate |
| 1192 | Hazard Pay | M140 | $/hr or % premium |
| 1193 | Travel Pay | M110 | Hours x rate for travel time |
| 1194 | Tool Allowance | M260 | Fixed per-period amount |

### Retail / Hospitality
| WT | Description | Model | Calculation |
|----|-------------|-------|-------------|
| 1200 | Tip Wages (Reported) | M210 | EE-reported tips (taxable) |
| 1201 | Tip Credit | M100 | Employer tip credit offset |
| 1202 | Service Charge | M210 | Mandatory service charges |
| 1203 | Split Shift Premium | M140 | CA: 1 hr min wage for split shifts |

### Additional Deductions
| WT | Description | Model | Pre/Post Tax |
|----|-------------|-------|-------------|
| 2082 | HSA EE Contribution | D300 | Pre-tax (IRC §223) |
| 2095 | Parking Pre-Tax | D500 | Pre-tax (IRC §132) |
| 2096 | Transit Pre-Tax | D500 | Pre-tax (IRC §132) |
| 2100-2105 | Garnishment WTs | System | Post-tax (involuntary) |
| 2130 | Union Dues | D500 | Post-tax |
| 2131 | Union Assessment | D500 | Post-tax (one-time) |

### Additional ER Contributions
| WT | Description | Model | Calculation |
|----|-------------|-------|-------------|
| 3055 | ER HSA Contribution | E200 | Flat per enrollment tier |
| 3090 | ER Union H&W | E300 | $/hour worked (per CBA) |
| 3095 | ER Union Pension | E300 | $/hour or % gross (per CBA) |

## Wage Type Permissibility (V_T511)

Controls which EE subgroups can receive each wage type. Set per EE subgroup grouping:
| WT Category | 01 Sal Exempt | 02 Hrly Non-Ex | 03 Executive | 04 PT Hourly | 05 Temp |
|-------------|:---:|:---:|:---:|:---:|:---:|
| 1000 Base Salary | ✓ | - | ✓ | - | - |
| 1010 Regular Hours | - | ✓ | - | ✓ | ✓ |
| 1020 OT 1.5x | - | ✓ | - | ✓ | ✓ |
| 1040 Shift Diff | - | ✓ | - | ✓ | ✓ |
| 1100 Annual Bonus | ✓ | ✓ | ✓ | - | - |
| 2070 401(k) | ✓ | ✓ | ✓ | - | - |
| 2130 Union Dues | - | ✓ | - | ✓ | - |

## Cumulation Configuration (V_T54C1)

| Cumulation WT | Description | Source WTs |
|---------------|-------------|-----------|
| /300 | Total Gross | All 1000-series earnings |
| /301 | Total Net Pay | After all deductions |
| /302 | Total Taxable Gross | /300 minus pre-tax deductions |
| /310 | Total EE Deductions | All 2000-series |
| /320 | Total ER Contributions | All 3000-series |
| /330 | Total Tax Withholdings | /101-/112 |
| /340 | Regular Earnings | 1000, 1010, 1060-1090 |
| /350 | OT Earnings | 1020, 1030, 1050 |
| /360 | Supplemental Earnings | 1100-1170 |

## IRS Limits (Update Annually)
| Limit | 2025 Amount | 2026 Amount (Projected) |
|-------|-------------|------------------------|
| SS Wage Base | $168,600 | $174,900 |
| 401(k) Deferral | $23,500 | $23,500 |
| 401(k) Catch-Up (50+) | $7,500 | $7,500 |
| 401(k) Super Catch-Up (60-63) | $11,250 | $11,250 |
| Total 415 Limit (EE+ER) | $70,000 | $70,000 |
| FSA Medical | $3,200 | $3,300 |
| FSA Carryover | $640 | $640 |
| FSA Dep Care | $5,000 | $5,000 |
| HSA Self | $4,150 | $4,300 |
| HSA Family | $8,300 | $8,550 |
| HSA Catch-Up (55+) | $1,000 | $1,000 |
| Group Life Non-Taxable | $50,000 | $50,000 |
| Tuition Reimb Non-Taxable | $5,250 | $5,250 |
| Transit/Parking Pre-Tax | $315/mo | $325/mo |
| HCE Compensation | $155,000 | $160,000 |
