# Enterprise Structure Reference

## Company Code (T001)
- One company code per legal entity
- Drives: fiscal year variant, chart of accounts, currency
- SAP Table: T001
- IMG: Enterprise Structure > Definition > Financial Accounting

## Personnel Area (T001P)
- Represents a physical location or significant organizational unit
- Assigned to exactly one company code (T500P)
- Drives: holiday calendar, default work schedule, tax jurisdiction
- SAP Table: T001P
- IMG: Enterprise Structure > Definition > HCM > Personnel Areas

### Common PA Pattern (US Multi-Site)
| PA Code | Description | State | Holiday Calendar |
|---------|-------------|-------|-----------------|
| 1000 | Corporate HQ | varies | US + state holidays |
| 1100 | Manufacturing Plant 1 | varies | US + state + plant shutdown |
| 2000 | Regional Office | varies | US + state holidays |
| 3000 | Distribution Center | varies | US + state holidays |

## Personnel Subarea (T001P subtypes)
- Functional subdivision within a PA
- Drives: pay scale area/type, wage type permissibility, absence quotas, work schedule rules
- SAP Table: T001P (subarea fields)
- IMG: Enterprise Structure > Definition > HCM > Personnel Subareas

### Common PSA Pattern
| PSA Code | Description | Typical Usage |
|----------|-------------|---------------|
| 0001 | Corporate Office / Admin | Salaried office workers |
| 0002 | Production / Warehouse | Hourly production staff |
| 0003 | Sales / Field | Sales reps, field service |
| 0004 | Executive / Management | C-suite, VPs, Directors |

### PSA Groupings (Critical for Payroll)
Each PSA must be assigned to groupings that control:
- **Pay scale grouping** (V_001P_C): Which pay scale structure applies
- **Wage type grouping** (V_001P_B): Which wage types are permitted
- **Absence grouping**: Which absence types and quotas apply
- **Work schedule grouping**: Default daily/weekly work schedules

## Employee Group (T501)
- Broad classification of the employment relationship
- SAP Table: T501
- IMG: Personnel Management > PA > Org Data > Define Employee Groups

### Standard EE Groups
| Code | Description | Payroll Processing |
|------|-------------|-------------------|
| 1 | Active | Yes |
| 2 | Retiree | No (or benefit-only) |
| 9 | External / Contractor | No |

## Employee Subgroup (T503K)
- Detailed classification within an EE Group
- Drives: FLSA status, default payroll area, wage type permissibility
- SAP Table: T503K (linked to T503 for EE Group + Subgroup combinations)
- IMG: Personnel Management > PA > Org Data > Define Employee Subgroups

### Standard EE Subgroups (US)
| Code | Description | FLSA | Default Pay Area | Time Recording |
|------|-------------|------|-----------------|----------------|
| 01 | Salaried Exempt | Exempt | Biweekly | Negative |
| 02 | Hourly Non-Exempt | Non-Exempt | Weekly | Positive |
| 03 | Executive | Exempt | Monthly | Negative |
| 04 | Part-Time Hourly | Non-Exempt | Weekly | Positive |
| 05 | Temporary | Non-Exempt | Weekly | Positive |

## Assignment Tables
- **T500P**: Personnel Area to Company Code
- **T001P**: Personnel Area + Subarea attributes
- **T503**: Employee Group + Subgroup combinations (permissibility matrix)
- **Feature ABKRS**: Defaults payroll area from EE Group/Subgroup/PA/PSA

## Holiday Calendar (SCAL)
- One calendar per state (or region) to capture state-specific holidays
- Assigned to Personnel Subarea
- Transaction: SCAL
- Consider: company-observed holidays vs. state/federal holidays
- Plant shutdown days can be added as special holiday entries

### US Federal Holidays (Typical)
New Year's Day, MLK Day, Presidents' Day, Memorial Day, Juneteenth, Independence Day, Labor Day, Columbus Day, Veterans Day, Thanksgiving, Christmas Day

## Work Schedule Rules
- Define daily work hours, break times, weekly patterns
- Assigned via PSA grouping + EE Subgroup
- Key variants:
  - NORM: Standard M-F 8-5 (40 hrs/week)
  - SHFT: Rotating shift schedule (3-shift)
  - FLEX: Flexible schedule (salaried/executive)
  - WARE: Warehouse schedule (variable shifts)
  - PART: Part-time schedule (< 30 hrs/week)

## Feature Configuration (PE03)

Features are decision trees that default values based on organizational assignment. Critical features for payroll:

### Feature ABKRS (Payroll Area Defaulting)
Defaults payroll area based on:
```
EE Group → EE Subgroup → Personnel Area → Personnel Subarea → Payroll Area
```
Example decision tree:
- EE Group 1 (Active) + EE Subgroup 01 (Sal Exempt) → Biweekly area
- EE Group 1 (Active) + EE Subgroup 02 (Hrly Non-Ex) → Weekly area
- EE Group 1 (Active) + EE Subgroup 03 (Executive) → Monthly area

### Feature SCHKZ (Work Schedule Rule Defaulting)
Defaults work schedule rule from PSA grouping + EE Subgroup.

### Feature LGMST (Legal Entity)
Defaults company code/legal entity from personnel area.

### Feature TARIF (Pay Scale)
Defaults pay scale type/area for pay scale-eligible employees.

### Feature PINCH (Incentive Wages)
Controls incentive wage processing by EE group.

## Union Configuration

### When Applicable
- Company has employees covered by collective bargaining agreements (CBA)
- Union dues deduction required (WT 2130)
- Union-specific benefits (H&W fund, pension)
- Union wage scales (pay scale configuration)

### SAP Objects
| Table | Purpose |
|-------|---------|
| T503 | EE Group + Subgroup combination with union indicator |
| IT0001 field | Personnel area/subarea with union assignment |
| Custom field | Union local code on IT0001 or IT0185 |

### Implementation Approach
1. Define EE Subgroups for union classifications (e.g., 06=Union Hourly, 07=Union Skilled)
2. Configure union dues deduction WT 2130 (permissible only for union subgroups)
3. Configure ER H&W contribution WT 3090 ($/hour per CBA)
4. Configure ER Pension contribution WT 3095 ($/hour or % per CBA)
5. Set up union wage scales in T510/T510N if CBA-defined rates
6. Configure separate benefit eligibility rules for union vs non-union
