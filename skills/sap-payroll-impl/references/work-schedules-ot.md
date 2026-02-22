# Work Schedule Rules & Overtime Reference

## Work Schedule Architecture

### SAP Tables
| Table | Purpose | Transaction |
|-------|---------|-------------|
| T508A | Work schedule rule definition | SM30 / SPRO |
| T550A | Daily work schedule (start/end/break times) | SM30 |
| T551A | Period work schedule (weekly/monthly pattern) | SM30 |
| T551C | Day type definitions (work day, day off, holiday) | SM30 |
| T552A | Absence counting rules (per WSR) | SM30 |
| T553A | Substitution types | SM30 |
| T554C | Shift definitions | SM30 |

### IMG Path
`Personnel Management > Personnel Time Management > Work Schedules`

## Standard Work Schedule Rules (US)

| WSR Code | Description | Daily Hours | Weekly Hours | Start | End | Break | Applicable To |
|----------|-------------|-------------|--------------|-------|-----|-------|--------------|
| NORM | Standard M-F 8-5 | 8.0 | 40.0 | 08:00 | 17:00 | 60 min | Salaried exempt, hourly office |
| SH01 | 1st Shift (Day) | 8.0 | 40.0 | 06:00 | 14:30 | 30 min | Production - day shift |
| SH02 | 2nd Shift (Swing) | 8.0 | 40.0 | 14:00 | 22:30 | 30 min | Production - swing shift |
| SH03 | 3rd Shift (Night) | 8.0 | 40.0 | 22:00 | 06:30 | 30 min | Production - night shift |
| SH12 | 12-Hour Day | 12.0 | 36/48 alt | 06:00 | 18:30 | 30 min | Healthcare, manufacturing |
| FLEX | Flexible (Exempt) | 8.0 | 40.0 | flex | flex | flex | Salaried exempt, executives |
| PART | Part-Time | 4.0-6.0 | 20-30 | varies | varies | varies | Part-time hourly |
| ONCL | On-Call | 0.0 (standby) | varies | N/A | N/A | N/A | Healthcare, utilities |
| R412 | Rotating 4-on/12h | 12.0 | 42 avg | varies | varies | 30 min | Continuous operations |

### Feature SCHKZ (Work Schedule Rule Defaulting)
Defaults WSR based on:
- Personnel Subarea grouping (V_001P_K)
- Employee Subgroup
- Decision tree: PSA → EE Subgroup → WSR assignment

## Overtime Rules by Jurisdiction

### Federal (FLSA)
| Rule | Threshold | Multiplier | Applies To | Week Definition |
|------|-----------|------------|-----------|-----------------|
| Weekly OT | >40 hours/week | 1.5x regular rate | Non-exempt only | Employer-defined 7-day period |
| No daily OT | N/A | N/A | N/A | N/A |

### California (Labor Code §510)
| Rule | Threshold | Multiplier | Applies To | Notes |
|------|-----------|------------|-----------|-------|
| Daily OT | >8 hours/day | 1.5x | Non-exempt | Most protective daily OT |
| Daily DT | >12 hours/day | 2.0x | Non-exempt | Applies to hours beyond 12 |
| Weekly OT | >40 hours/week | 1.5x | Non-exempt | After daily OT applied |
| 7th Day (first 8) | 7th consecutive day | 1.5x | Non-exempt | First 8 hours on 7th day |
| 7th Day (>8) | 7th day >8 hours | 2.0x | Non-exempt | Hours beyond 8 on 7th day |
| Alt Workweek | >10 hours/day (if elected) | 1.5x | Non-exempt | Requires 2/3 employee vote |

**CA Week Start**: SAP must track from Sunday unless alt workweek.
**CA Interaction**: Daily OT hours DO count toward 40-hour weekly threshold. Take the higher multiplier where both apply.
**CA Makeup Time**: Employees can voluntarily work >8 hours to make up missed time without OT (written request required).

### Colorado
| Rule | Threshold | Multiplier | Notes |
|------|-----------|------------|-------|
| Daily OT | >12 hours/day | 1.5x | Effective 2024+ |
| Weekly OT | >40 hours/week | 1.5x | Standard FLSA |

### Alaska
| Rule | Threshold | Multiplier | Notes |
|------|-----------|------------|-------|
| Daily OT | >8 hours/day | 1.5x | Similar to CA but no DT |
| Weekly OT | >40 hours/week | 1.5x | Standard FLSA |

### Nevada
| Rule | Threshold | Multiplier | Notes |
|------|-----------|------------|-------|
| Daily OT | >8 hours/day | 1.5x | If rate < 1.5x minimum wage |
| Weekly OT | >40 hours/week | 1.5x | Standard FLSA |

### All Other States
Follow FLSA weekly OT only (>40 hours/week = 1.5x). No daily OT requirement.

## Shift Differential Configuration

### Standard Shift Premiums
| Shift | Typical Premium | Calculation Method | Wage Type |
|-------|----------------|-------------------|-----------|
| 1st (Day) | No premium | Base rate | 1010 |
| 2nd (Swing) | $1.00-3.00/hr or 5-10% | $/hr add-on or % of base | 1040 |
| 3rd (Night) | $1.50-4.00/hr or 8-15% | $/hr add-on or % of base | 1041 |
| Weekend | $0.50-2.00/hr | $/hr add-on | 1042 (custom) |
| Holiday | 1.5x-2.0x base | Multiplier | 1050 |

### Shift Determination Methods
1. **Time-based**: Automatic from work schedule rule (shift start/end times)
2. **Substitution-based**: From IT2003 (shift substitution record)
3. **Time entry-based**: Imported from external time system (Kronos, ADP)
4. **Manual**: Manager assignment via PA41

### SAP Shift Premium Processing
- Time evaluation (RPTIME00/PT60) determines shift from actual clock times
- PCR assigns shift differential WT based on majority-of-hours rule or actual-hours rule
- Majority rule: If >50% of hours fall in 2nd shift window → entire shift gets 2nd shift premium
- Actual hours rule: Only hours actually in 2nd/3rd shift window get premium

## Weighted Average OT Rate

For employees with multiple pay rates in a week (e.g., regular rate + shift premium):
```
Weighted Average Rate = Total straight-time earnings / Total hours worked
OT Premium = (Weighted Average Rate × 0.5) × OT hours
```
This is FLSA-required when an employee earns different rates in the same week.

## Meal & Rest Break Rules (State-Specific)

| State | Meal Break | Rest Break | Penalty for Violation |
|-------|-----------|------------|----------------------|
| CA | 30 min unpaid for >5 hrs; 2nd for >10 hrs | 10 min paid per 4 hrs | 1 hour pay penalty each |
| NY | 30 min for shifts >6 hrs | No state requirement | Employer fine |
| IL | 20 min for shifts ≥7.5 hrs | No state requirement | Employer fine |
| WA | 30 min for shifts >5 hrs | 10 min paid per 4 hrs | 1 hour pay penalty (CA-style) |
| Federal | No requirement | No requirement | N/A |

**SAP Implementation**: Break violations can generate penalty wage types via custom PCR in time evaluation.

## Holiday Pay Rules

### Standard Holiday Premium Patterns
| Scenario | Calculation | Wage Type |
|----------|------------|-----------|
| Holiday worked (non-exempt) | Regular rate × hours + holiday premium × hours | 1010 + 1050 |
| Holiday not worked (eligible) | 8 hours at regular rate | 1060 (PTO/Holiday) |
| Holiday worked (shift) | Regular rate × hours + shift diff + holiday premium | 1010 + 1040/1041 + 1050 |
| Holiday OT | Holiday premium + OT premium (higher rate wins) | Per company policy |

### Union Holiday Rules
Union CBAs often specify:
- Double time for all holiday work
- Triple time for certain holidays (Christmas, Thanksgiving)
- Premium applies to full shift regardless of hours worked
- Callback minimums (4-hour minimum for holiday callback)
