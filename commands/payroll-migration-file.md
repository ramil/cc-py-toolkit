---
description: Generate hiring data migration file from config workbook
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, TodoWrite
argument-hint: <config-workbook.xlsx>
---

Generate a SAP HCM Payroll Hiring Data Migration File from a Configuration Workbook. This file provides a ready-to-use LSMW/HRCM import template pre-populated with sample employee records whose values align with the configuration workbook.

**The config workbook is the input.** Every employee record value (org assignment, wage type, tax area, benefit plan, etc.) must use valid codes from the config workbook tabs. This ensures the migration file is immediately usable for data loading without value mismatches.

Read the skill file at `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/SKILL.md` first. Then read the data migration reference from `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/references/data-migration.md` for infotype loading order and migration best practices.

## Input

The user must provide a configuration workbook .xlsx file (via upload or file path). If no file is provided, ask the user to upload or specify the path.

Read and parse the config workbook to extract all valid configuration values from each tab:
- **Tab 1 (Enterprise Structure)**: PA codes, PSA codes, EE Group codes, EE Subgroup codes
- **Tab 3 (Payroll Areas)**: Payroll area codes and descriptions
- **Tab 4 (Work Schedule Rules)**: WSR codes by EE type
- **Tab 5 (Wage Type Catalog)**: All wage type codes, categories, amounts
- **Tab 7 (Pay Scale Structure)**: Pay scale types, areas, groups, levels (if present)
- **Tab 8 (Tax Authorities)**: State codes, tax jurisdictions, BSI geocodes
- **Tab 9 (Absence & Quota)**: Absence types, quota types
- **Tab 14 (Benefits Config)**: Benefit plan codes, eligibility rules

Use AskUserQuestion to ask:
1. How many sample employees should be generated? (Default: 10-15 covering all employee types and states)
2. Should the file include realistic synthetic data (names, addresses, SSNs) or use obvious placeholders (Employee_001, 000-00-0001)?
3. Are there specific employee scenarios to include? (e.g., union employee, multi-state worker, garnishment recipient, new hire with prior employer YTD)

## CRITICAL GENERATION REQUIREMENTS

**These requirements are NON-NEGOTIABLE. Every migration file MUST meet ALL of these.**

### Minimum Employee Count: 12
Generate at least 12 employees. NEVER generate fewer than 10. The scenarios list above provides 10 types — add 2-3 more to cover remaining PA/PSA combinations.

### Benefits Infotype Sheets: MANDATORY for Full/Hybrid Approach
If benefits_approach = "full" or "hybrid", you MUST generate ALL of these sheets:
- **IT0167 (Health Plans)**: Medical + Dental + Vision = 3 rows per eligible employee
- **IT0168 (Insurance Plans)**: Life + STD + LTD = 2-3 rows per eligible employee
- **IT0169 (Savings Plans)**: 401k = 1 row per eligible employee
- **IT0171 (General Benefits)**: FSA/HSA = 1 row per eligible employee
**This is the #1 most common failure.** These 4 sheets are frequently skipped entirely. They MUST exist.

### IT0003 (Payroll Status): MANDATORY
Every employee MUST have 1 row in IT0003 with ABKRS matching their IT0001 payroll area.

### IT0194 (Garnishment Order): MANDATORY if garnishments=True
If the company profile says garnishments=True, you MUST generate at least 1-2 IT0194 rows for a test garnishment employee.

### IT0559 (Tax YTD): MANDATORY if mid_year=True
If the company profile says mid_year=True, you MUST generate IT0559 rows for at least 2 mid-year hire employees.

### Data Quality Review Sheet: MANDATORY
ALWAYS generate a "Data_Quality_Review" sheet with AI findings. This is a critical deliverable, not optional.

### Cover/Summary Sheet: MANDATORY
ALWAYS generate a Cover/Index sheet as the first tab with employee roster and loading order.

### Minimum Sheet Count: 18
The migration file MUST have at least 18 sheets (including Cover + Data Quality Review + all IT sheets).

### ⚠️ CORE INFOTYPES ARE ALWAYS REQUIRED — NO EXCEPTIONS
The following infotype sheets MUST exist in EVERY migration file regardless of Benefits, Time, or OM approach:

**ALWAYS GENERATE THESE 14 CORE SHEETS (plus Cover + Data Quality Review = 16 minimum):**
1. IT0000 (Actions) — ALWAYS
2. IT0001 (Org Assignment) — ALWAYS — MUST contain ALL PA codes from config
3. IT0002 (Personal Data) — ALWAYS
4. IT0003 (Payroll Status) — ALWAYS — 1 row per employee
5. IT0006 (Addresses) — ALWAYS
6. IT0007 (Planned Working Time) — ALWAYS — ZTEFN varies by time approach
7. IT0008 (Basic Pay) — ALWAYS
8. IT0009 (Bank Details) — ALWAYS
9. IT0014 (Recurring Deductions) — ALWAYS — Min 3 rows/employee
10. IT0041 (Date Specifications) — ALWAYS — Min 2 rows/employee (SUBTY 01 + 03)
11. IT0105 (Communication) — ALWAYS — Email + phone
12. IT0207 (Residence Tax Area) — ALWAYS — Federal 00-000-0000 + state
13. IT0208 (Work Tax Area) — ALWAYS
14. IT0210 (W-4 Withholding) — ALWAYS — Min 2 rows/employee (Federal + state)

**CONDITIONAL SHEETS (add on top of the 14 core):**
- IT0167, IT0168, IT0169, IT0171 → Only if benefits_approach = "full" or "hybrid"
- IT0027 → Only if concurrent_employment = True
- IT0194 → Only if garnishments = True
- IT0559 → Only if mid_year = True
- IT2006 → Always (absence quotas)

**If your migration file is missing ANY of the 14 core sheets, it is INVALID.**

### ⚠️ ALL PERSONNEL AREAS IN IT0001
EVERY Personnel Area code from the config workbook Enterprise Structure tab MUST appear as a WERKS value in IT0001. Distribute employees across ALL PAs. If the company has 5 PAs, at least 5 different employees must each reference a different PA. This is checked automatically and is one of the top failure points.

### ⛔ MIGRATION FILE SELF-CHECK CHECKLIST (RUN BEFORE SAVING)
Before writing the .xlsx file, walk through EVERY item. Fix failures before saving:

1. **SHEET COUNT**: Count all sheets. Is it >= 18? Must have Cover + Data_Quality_Review + 14 core ITs + IT2006 + conditionals.
2. **COVER SHEET**: First tab must be "Cover" or "Summary" with employee roster and IT loading order.
3. **DATA QUALITY REVIEW**: Must have a "Data_Quality_Review" sheet with AI validation findings.
4. **EMPLOYEE COUNT**: Does IT0001 have >= 12 data rows (one per employee)?
5. **IT0000 (Actions)**: Every employee has a hiring action (MASSN=01).
6. **IT0001 (Org Assignment)**: EVERY PA code from config appears as WERKS. Check: list all unique WERKS values — do they match ALL PA codes?
7. **IT0003 (Payroll Status)**: One row per employee. ABKRS matches their payroll area.
8. **IT0007 (Planned Working Time)**: ZTEFN column exists. If time_approach="negative" or "third_party", ALL values must be 9. If time_approach="full", hourly=1, salaried=9.
9. **IT0014 (Recurring Deductions)**: Total rows / employee count >= 3. Each employee needs Medical(2100) + 401k(2120) + at least 1 more.
10. **IT0041 (Date Specifications)**: Total rows / employee count >= 2. Each employee needs SUBTY=01 (Orig Hire) + SUBTY=03 (Seniority).
11. **IT0105 (Communication)**: One row per employee with email address.
12. **IT0207 (Residence Tax)**: EVERY employee has Federal geocode "00-000-0000" as one row + state geocode "XX-XXX-XXXX" as another. The TXJCD column must ONLY contain XX-XXX-XXXX format values — NEVER text like "Federal" or "State".
13. **IT0208 (Work Tax)**: Same format as IT0207. Federal 00-000-0000 + state geocode.
14. **IT0210 (W-4 Withholding)**: Total rows / employee count >= 2. Each employee needs SUBTY=01 (Federal) + SUBTY=02 (State). TXJCD must be in XX-XXX-XXXX format.
15. **IT0194 (Garnishment)**: If company has garnishments=True, this sheet MUST exist with at least 1 garnishment order for a test employee.
16. **IT0559 (Tax YTD)**: If company has mid_year=True, this sheet MUST exist with YTD balances for at least 2 employees.
17. **IT2006 (Absence Quotas)**: ALWAYS generate this sheet. At least 1 row per employee (opening PTO balance).
18. **IT0167/0168/0169/0171 (Benefits)**: If benefits_approach="full" or "hybrid", ALL 4 must exist with data. If "deductions_only", SKIP these entirely.
19. **IT0027 (Cost Distribution)**: If concurrent_employment=True, this sheet MUST exist.
20. **UNION EMPLOYEES**: If the company has unions, at least 1 employee must have "UNION" or "CBA" or "DUES" referenced in their data (IT0014 row with WT 2150 Union Dues).
21. **ALL STATES**: Every state in the company profile must appear in IT0207/IT0208 geocodes.
22. **GEOCODE FORMAT**: EVERY TXJCD value in IT0207, IT0208, IT0210 must be in XX-XXX-XXXX format. Federal=00-000-0000, States use their BSI code (e.g., NY=33-000-0000, CA=06-000-0000, TX=43-000-0000, FL=12-000-0000, IL=17-000-0000, PA=39-000-0000, OH=36-000-0000, WA=48-000-0000, OR=38-000-0000, CO=08-000-0000, AZ=04-000-0000, MN=27-000-0000, GA=13-000-0000, NJ=34-000-0000, MA=25-000-0000, MI=26-000-0000, VA=47-000-0000, NC=34-000-0000, WI=49-000-0000, MD=24-000-0000).

### BSI Geocode Reference Table
Use these exact codes for common states in TXJCD columns:
| State | BSI Geocode | State | BSI Geocode |
|-------|-------------|-------|-------------|
| Federal | 00-000-0000 | NY | 33-000-0000 |
| CA | 06-000-0000 | TX | 43-000-0000 |
| FL | 12-000-0000 | IL | 17-000-0000 |
| PA | 39-000-0000 | OH | 36-000-0000 |
| WA | 48-000-0000 | OR | 38-000-0000 |
| CO | 08-000-0000 | AZ | 04-000-0000 |
| MN | 27-000-0000 | GA | 13-000-0000 |
| NJ | 34-000-0000 | MA | 25-000-0000 |
| MI | 26-000-0000 | VA | 47-000-0000 |
| NC | 28-000-0000 | WI | 49-000-0000 |
| MD | 24-000-0000 | IN | 18-000-0000 |
| TN | 42-000-0000 | MO | 29-000-0000 |
**NEVER use state abbreviations or words like "Federal" in TXJCD — ONLY the XX-XXX-XXXX numeric format.**

## AI-Powered Employee Scenario Planning

Before generating employee records, use the LLM to intelligently plan the employee scenarios:

### AI Scenario Planner
Pass the full config workbook summary to the AI and ask it to plan 12-18 employee scenarios that **collectively cover ALL configured elements**. The AI should ensure:
1. Every PA/PSA is used at least once
2. Every payroll area has at least one employee
3. Every EE Subgroup has at least one employee
4. Every operating state has at least one employee
5. Multi-state scenario exists (residence state ≠ work state)
6. CA employees test daily OT rules
7. Union employees test dues + H&W + pension deductions
8. At least one garnishment recipient
9. At least one mid-year hire (for IT0559 YTD testing)
10. At least one executive (for SS wage base cap, Additional Medicare, high 401k)
11. At least one part-time employee (for benefits eligibility testing)
12. At least one employee per shift (if shifts are configured)

The AI generates a JSON scenario plan with: employee name, EE Group/Subgroup, PA/PSA, state, payroll area, WSR, pay type/rate, deductions, benefits, special attributes.

### AI Data Review
After generating all migration data, pass a summary to the AI for a quality review:
- Salary reasonableness (executives $150K+, hourly $15-45/hr, part-time proportional)
- Tax area alignment (IT0207 residence matches IT0006 address state)
- Benefits eligibility (part-time/temp shouldn't have FT-only benefits)
- Deduction limits (401k ≤ $23,500, FSA ≤ $3,300)
- Multi-row completeness (IT0014 has 3-6 rows per employee, IT0210 has Federal + state rows)
- Union employees have union-specific WTs (2130 dues, IT0167-0171 union H&W)

Insert the AI review findings as a "Data Quality Review" sheet in the migration file with: Finding ID | Severity | Employee | Infotype | Issue | Resolution.

## Approach-Driven Migration Scope

**Before generating infotype sheets, read the config workbook cover sheet or funcspec to determine the approach decisions. These control which sheets are generated:**

### Benefits Approach
- **Full SAP Benefits** → Generate IT0167, IT0168, IT0169, IT0171 with full plan enrollment data. IT0014 contains only non-benefit deductions (garnishments, union dues, misc).
- **Deductions Only (IT0014)** → **SKIP IT0167, IT0168, IT0169, IT0171 entirely.** All benefit deductions (medical, dental, vision, 401k, FSA, HSA, life, STD, LTD) are loaded as IT0014 recurring deduction rows. A typical employee will have 6-10 IT0014 rows instead of 3-4. The IT0014 sheet becomes the primary benefits carrier.
- **Hybrid** → Generate only the SAP-managed benefit infotypes (e.g., IT0169 for 401k). External benefits go into IT0014.

### Time Management Approach
- **Full Time Eval** → IT0007 has ZTEFN=1 (time eval active) for hourly employees. Include IT0315 (Time Sheet Defaults) if CATS is used.
- **Negative Time Only** → IT0007 has ZTEFN=9 (no time eval) for ALL employees. Planned working time equals actual time unless absence is recorded.
- **3rd-Party Time Import** → IT0007 has ZTEFN=9. Time data arrives via interface, not via migration file.

### OM Scope
- **Full/Minimal OM** → IT0001 ORGEH and PLANS fields are populated with org unit and position IDs.
- **No OM** → IT0001 ORGEH and PLANS fields are blank or "99999999". KOSTL (cost center) is the primary organizational reference.

### Concurrent Employment
- **Yes** → IT0000 includes concurrent employment action types. Multiple IT0001 records per employee (different positions). IT0027 (Cost Distribution) sheet is generated.
- **No** → Standard single-record approach.

## Config-to-Migration Mapping

Generate one Excel tab per SAP infotype, in the **mandatory loading order**:

| Tab/Sheet | SAP Infotype | Description | Source Config Tab(s) | Conditional |
|---|---|---|---|---|
| 1. IT0000 | Actions | Hiring action record | Enterprise Structure | Always |
| 2. IT0001 | Org Assignment | Company code, PA, PSA, EE Group/Subgroup, payroll area | Enterprise Structure, Payroll Areas, Feature Config | Always |
| 3. IT0002 | Personal Data | Name, DOB, gender, nationality, marital status | (Synthetic data) | Always |
| 4. IT0003 | Payroll Status | Payroll area lock indicator, earliest retro date | Payroll Areas | Always |
| 5. IT0006 | Addresses | Street, city, state, zip, country | Tax Authorities (align states) | Always |
| 6. IT0007 | Planned Working Time | Work schedule rule, employment %, time mgmt status | Work Schedule Rules | Always |
| 7. IT0008 | Basic Pay | Pay scale or direct pay, wage type, amount, currency | Wage Type Catalog, Pay Scale | Always |
| 8. IT0009 | Bank Details | Bank key, account number, payment method | (Template values) | Always |
| 9. IT0014 | Recurring Deductions | Pre-tax/post-tax deductions, amounts | Wage Type Catalog (deduction WTs) | Always |
| 10. IT0041 | Date Specifications | Seniority date, benefits eligibility date, orig hire date | (Calculated from hire date) | Always |
| 11. IT0105 | Communication | Email address, work phone | (Synthetic data) | Always |
| 12. IT0207 | Residence Tax Area | Tax authority code based on home address state/locality | Tax Authorities | Always |
| 13. IT0208 | Work Tax Area | Tax authority code based on work location | Tax Authorities | Always |
| 14. IT0210 | Tax Withholding (W-4) | Filing status, dependents, additional withholding per authority | Tax Authorities | Always |
| 15. IT0167 | Health Plans | Medical, dental, vision enrollment | Benefits Config | **Only if Full/Hybrid Benefits** |
| 16. IT0168 | Insurance Plans | Life, AD&D, STD, LTD enrollment | Benefits Config | **Only if Full/Hybrid Benefits** |
| 17. IT0169 | Savings Plans | 401k, Roth 401k enrollment with contribution % | Benefits Config | **Only if Full/Hybrid Benefits** |
| 18. IT0171 | General Benefits | FSA, HSA, other benefit enrollments | Benefits Config | **Only if Full/Hybrid Benefits** |
| 19. IT0027 | Cost Distribution | Multi-cost-center allocation % | Enterprise Structure | **Only if Concurrent Employment** |
| 20. IT0194 | Garnishment Order | Court order details (for garnishment test employees) | Garnishment Config | If garnishments exist |
| 21. IT0559 | Tax YTD Balances | YTD accumulators (for mid-year go-live scenarios) | Tax Authorities | **Only if mid-year go-live** |
| 22. IT2006 | Absence Quotas | PTO/sick leave opening balances | Absence & Quota Config | Always |

## Employee Scenario Coverage

Generate employees that cover ALL configured scenarios. At minimum include:

1. **Salaried Exempt** — Monthly pay, standard work schedule, HQ state
2. **Hourly Non-Exempt** — Biweekly, overtime eligible, different state
3. **Part-Time Hourly** — Reduced schedule, pro-rated benefits
4. **California Employee** — Daily OT rules, CA SDI, CA PFL (if CA is a configured state)
5. **Multi-State Worker** — Residence state ≠ work state, reciprocity if applicable
6. **Union Employee** — Union subgroup, CBA pay scale, union benefits (if union configured)
7. **Executive** — Executive subgroup, supplemental compensation
8. **New Hire (Mid-Year)** — Start date mid-year, prior employer YTD (IT0560)
9. **Garnishment Recipient** — Active child support order for garnishment testing
10. **Shift Worker** — 2nd or 3rd shift, shift differential (if shifts configured)

For each employee, populate ALL applicable infotype sheets with consistent, cross-referenced data. For example:
- IT0001 org assignment values must match Tab 1 (Enterprise Structure) codes
- IT0008 wage types must exist in Tab 5 (Wage Type Catalog)
- IT0207/0208 tax areas must match Tab 8 (Tax Authorities) codes
- IT0167-0171 benefit plans must match Tab 14 (Benefits Config) codes
- IT0007 work schedule rule must match Tab 4 (Work Schedule Rules)

## CRITICAL GENERATION RULES

### ABSOLUTE REQUIREMENTS (violations = invalid output)

1. **EVERY infotype sheet MUST have BEGDA (Start Date) and ENDDA (End Date) columns.** These are the #1 most common missing fields. Format: YYYY-MM-DD. ENDDA = 9999-12-31 for open-ended records. BEGDA = hiring date (typically go-live date).
2. **Use EXACT SAP technical field names as column headers.** The header row (Row 3) must use the SAP field names shown in the tables below (PERNR, BEGDA, ENDDA, MASSN, MASSG, BUKRS, WERKS, BTRTL, etc.) — NOT business descriptions. Add a business-friendly description in Row 2 (merged) for human readability, but the actual column headers in Row 3 must be SAP field names.
3. **Multi-row infotypes:** IT0014, IT0167, IT0168, IT0169, IT0171, IT0207, IT0208, IT0210, IT0559, and IT2006 require MULTIPLE ROWS per employee. Generate one row per deduction, one row per benefit plan, one row per tax authority, one row per absence type. A typical employee has 15-25 total rows across all infotype sheets.
4. **ALL 18 infotype sheets are MANDATORY in the output.** Do not skip any infotype. Even if only 1-2 employees qualify for a given sheet (e.g., IT0194 Garnishments), the sheet must still exist with its proper header row.
5. **No invented/fake SAP field names.** Every column header must be a real SAP HCM field name from the PA/PD infotype structure. If unsure of the exact SAP field name, use the business name in parentheses after the field — e.g., "FAMST (Marital Status)" — but the primary header text must be the SAP field.
6. **Row 1 = Sheet title (merged, 14pt bold): "IT0000 — Actions" etc. Row 2 = SAP description + LSMW object (merged, 10pt italic). Row 3 = SAP field name headers (navy fill, white text). Data starts at Row 4.**
7. **No combined/concatenated values.** Each SAP field gets its own column.
8. **Config workbook traceability:** Green fill (#E8F5E9) = value from config workbook. Yellow fill (#FFFFF0) = requires manual input. Red fill = placeholder/TBD.

### COMMON MISTAKES TO AVOID
- ❌ Omitting BEGDA/ENDDA — EVERY infotype needs them
- ❌ Using BTRTL for Personnel Area (BTRTL = Personnel Subarea, WERKS = Personnel Area)
- ❌ Inventing field names with "ESSION" suffix (BEESSION, AESSION, KESSION, GESSION, PEESSION, REESSION, LOESSION, FESSION, MESSION, TAESSION, LNESSION, BESSION) — NONE of these are real SAP fields. Use the EXACT field names from the tables below.
- ❌ Missing entire infotype sheets (especially IT0167, IT0168, IT0169, IT0171, IT0559)
- ❌ Using text codes for LGART (wage types must be 4-digit numeric: 1000, 2100, etc.)
- ❌ Fewer than 3 rows per employee on IT0014 (most employees have 4-6 deductions)
- ❌ Single row per employee on IT0210 (minimum 2: Federal + state)
- ❌ Putting payroll area in PLANS field (payroll area = ABKRS)

### All PAs MUST Be Used in IT0001
EVERY Personnel Area code from the config workbook MUST appear in IT0001. If the company has PAs ["NTL1", "NTL2", "NTL3", "NTL4", "NTL5"], distribute employees across ALL 5 PAs. Missing PA = untested configuration.

### IT0210 Withholding: MINIMUM 2 Rows Per Employee
Every single employee MUST have at minimum:
- Row 1: SUBTY=01, TXJCD=00-000-0000 (Federal W-4)
- Row 2: SUBTY=02, TXJCD=[state geocode] (State withholding)
**Single-row IT0210 = payroll WILL NOT calculate taxes.**

### IT0041 Date Specifications: MINIMUM 2 Rows Per Employee
Every single employee MUST have:
- Row 1: SUBTY=01 (Original Hire Date)
- Row 2: SUBTY=03 (Seniority Date)
**Single-row IT0041 = PTO accrual tiers won't work.**

### Federal Geocode 00-000-0000: MANDATORY for ALL Employees
In IT0207, IT0208, AND IT0210, EVERY employee MUST have a row with TXJCD="00-000-0000" for Federal. This is the #1 tax calculation requirement. Without it, NO federal taxes calculate.

### TOP 5 FAILURE POINTS (from exhaustive testing — address these FIRST)

1. **🔴 FEDERAL GEOCODE 00-000-0000 MISSING** — The #1 failure. EVERY employee MUST have "00-000-0000" as a TXJCD value in IT0207, IT0208, AND IT0210. This is the Federal tax jurisdiction. Without it, no federal tax will calculate. Generate it explicitly for every employee as the FIRST tax row.

2. **🔴 IT0014 INSUFFICIENT DEDUCTIONS** — Each employee MUST have at least 2-3 IT0014 rows (e.g., Medical + 401k + Dental). A single deduction row per employee is NOT sufficient.

3. **🔴 PA CODES MISSING FROM IT0001 WERKS** — The WERKS column in IT0001 MUST use the EXACT Personnel Area codes from the config workbook (e.g., "MHS1", "PWG3", "NTL5"). Do NOT use generic codes like "1000" or "1001" — use the actual PA codes that appear in the Enterprise Structure tab of the config workbook.

4. **🔴 IT0210 INSUFFICIENT TAX ROWS** — Each employee MUST have at minimum 2 rows in IT0210: one for Federal (SUBTY=01, TXJCD="00-000-0000") and one for their State (SUBTY=02). Without both rows, withholding won't calculate.

5. **🔴 EMPTY INFOTYPE SHEETS** — Every IT sheet MUST have data rows. If a sheet is created but has 0 data rows (only headers), the migration file is invalid. Use the two-pass approach to prevent this.

6. **🔴 BENEFITS APPROACH CONSISTENCY** — If the config workbook uses "Deductions Only" benefits approach, do NOT generate IT0167/IT0168/IT0169/IT0171 sheets. Instead, load ALL benefit deductions into IT0014. Generating benefit plan sheets when the client uses external benefits creates data that cannot be loaded.

7. **🔴 MISSING IT0003/IT0041/IT0105** — These three infotypes are commonly forgotten but needed for go-live: IT0003 (Payroll Status) ensures correct payroll area assignment, IT0041 (Date Specifications) captures seniority dates for PTO accrual, IT0105 (Communication) provides email for ESS payslip distribution.

8. **🔴 IT0007 ZTEFN MUST MATCH TIME APPROACH** — If Negative Time Only or 3rd-Party Time Import, ALL employees must have ZTEFN=9 (no time evaluation). Only set ZTEFN=1 if Full SAP Time Evaluation is configured. Wrong ZTEFN = payroll errors or missing time data.

## Column Definitions Per Sheet (SAP Technical Field Names)

### IT0000 — Actions
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | 8-digit (00000001) |
| B | BEGDA | Start Date | R | YYYY-MM-DD (hire date) |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | MASSN | Action Type | R | 01 = Hiring |
| E | MASSG | Action Reason | R | 01 = New Hire, 02 = Rehire |
| F | STAT2 | Employment Status | R | 3 = Active |
| G | PERSG | Employee Group | R | From config Tab 1 (1, 2, 9) |
| H | PERSK | Employee Subgroup | R | From config Tab 1 (S1, U1, U2, etc.) |
| I | WERKS | Personnel Area | R | From config Tab 1 (SEA1, PDX1, etc.) |

### IT0001 — Organizational Assignment
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Start Date | R | YYYY-MM-DD |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | BUKRS | Company Code | R | From config (e.g., 1000) |
| E | WERKS | Personnel Area | R | From config Tab 1 |
| F | BTRTL | Personnel Subarea | R | From config Tab 1 (PROD, ADMN, WHSE, etc.) — NOTE: BTRTL is PSA, not PA |
| G | PERSG | Employee Group | R | 1, 2, 9 |
| H | PERSK | Employee Subgroup | R | S1, U1, U2, U3, T1 |
| I | ABKRS | Payroll Area | R | From config Tab 4 (W1, B1, etc.) — NOT the PLANS field |
| J | KOSTL | Cost Center | R | PA-based (e.g., SEA1-PROD, PDX1-ADMN) |
| K | ORGEH | Org Unit | O | Organizational unit ID |
| L | PLANS | Position | O | Position number |
| M | STELL | Job Key | O | Job code |

### IT0002 — Personal Data
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Start Date | R | YYYY-MM-DD |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | NACHN | Last Name | R | Realistic name |
| E | VORNA | First Name | R | Realistic name |
| F | MIDNM | Middle Name | O | Initial or blank |
| G | GBDAT | Date of Birth | R | YYYY-MM-DD (ages 22-65) |
| H | GESCH | Gender | R | 1 = Male, 2 = Female |
| I | FAMST | Marital Status | R | 0=Single, 1=Married, 2=Divorced, 3=Widowed |
| J | SINID | Social Security Number | R | Format: 900-XX-XXXX for test data (e.g., 900-01-0001) |
| K | NATIO | Nationality | R | US |
| L | SPRSL | Language | R | EN |

NOTE: SINID (Social Insurance ID) is the SAP field for SSN. Use 900-series test SSNs (IRS reserved for testing). Generate unique SSN for each test employee.

### IT0006 — Addresses
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | ANSSA | Address Type | R | 1 = Permanent Residence |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | STRAS | Street / House Number | R | Realistic address |
| F | ORT01 | City | R | |
| G | REGIO | State/Region | R | 2-letter state code (must match IT0207) |
| H | PSTLZ | Postal Code | R | 5-digit ZIP |
| I | LAND1 | Country | R | US |
| J | ORT02 | County | R | County name (needed for BSI geocode resolution) |
| K | TTEFN | Telephone | O | 10-digit |
| L | COM01 | Email | O | EE email |

### IT0007 — Planned Working Time
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Start Date | R | YYYY-MM-DD |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | SCHKZ | Work Schedule Rule | R | From config Tab 6 (1ST, 2ND, 3RD, NORM, PART) |
| E | EMPCT | Employment Percentage | R | 100 = full-time, 50-80 = part-time |
| F | MOSID | Employee Subgroup Grouping for WSR | R | Derived from PERSK grouping |
| G | ZTEFN | Time Management Status | R | 1 = Time eval active (hourly), 9 = No time eval (exempt) |
| H | SOLLZ | Daily Working Hours | R | Decimal: 8.00, 7.50, etc. Must match WSR |
| I | WKWDY | Weekly Workdays | R | 5 (standard), 6 (retail), etc. |
| J | ARBST | Weekly Working Hours | R | SOLLZ × WKWDY (e.g., 40.00) |

### IT0008 — Basic Pay
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Start Date | R | YYYY-MM-DD |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | LGA01 | Wage Type | R | 4-digit from config Tab 7 (1000=salary, 1010=hourly) |
| E | BET01 | Amount | R | Salary: annual amount. Hourly: hourly rate |
| F | ANCUR | Currency | R | USD |
| G | ANSAL | Annual Salary | R | Calculated: hourly × 2080, or direct if salaried |
| H | DIVGV | Pay Scale Type | O | Only for union/CBA EEs (from config Tab 10) |
| I | TRFAR | Pay Scale Area | O | Only for union/CBA EEs |
| J | TRFGB | Pay Scale Group | O | Only for union/CBA EEs |
| K | TRFST | Pay Scale Level | O | Only for union/CBA EEs |
| L | LGTYP | Wage Type Indicator | O | 10 = annual, 20 = monthly, 30 = biweekly, 40 = hourly |

NOTE: BET01/LGA01 is the standard pay component pair. If multiple pay components exist, add LGA02/BET02 columns.

### IT0009 — Bank Details
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | SUBTY | Subtype | R | 0 = Main bank |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | BANKS | Bank Country | R | US |
| F | BANKL | Bank Routing Number | R | 9-digit (placeholder: 000000000) |
| G | BANKN | Bank Account Number | R | Placeholder: PLACEHOLDER_XXXX |
| H | EMFTX | Bank Name | O | e.g., Wells Fargo |
| I | ZLSCH | Payment Method | R | T = ACH/Direct Deposit, C = Check |
| J | BTEFN_PCT | Percentage | O | 100 = full amount to this account |

### IT0003 — Payroll Status
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Start Date | R | YYYY-MM-DD (hire date) |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | ABKRS | Payroll Area | R | From config Tab 4 (must match IT0001) |
| E | DTEFN | Earliest Retro Date | R | YYYY-MM-DD (typically go-live date or 6 months prior) |
| F | DTEFN_MD | Payroll Correction Flag | O | Blank = normal |

ONE ROW PER EMPLOYEE. Payroll status is auto-created during hiring action but MUST be verified — ensures employee is assigned to correct payroll area and retro limits are set.

### IT0041 — Date Specifications
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | SUBTY | Date Type | R | 01=Original Hire, 03=Seniority, 08=Benefits Eligibility, 12=Company Seniority |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | DAT01 | Date Value | R | YYYY-MM-DD — the actual date being recorded |

**MULTIPLE ROWS per employee (minimum 2-3):**
- Row 1: SUBTY=01 Original Hire Date (DAT01 = hire date; for rehires = original first hire)
- Row 2: SUBTY=03 Seniority Date (DAT01 = date for PTO accrual tier calculation)
- Row 3: SUBTY=08 Benefits Eligibility Date (DAT01 = hire date + waiting period)
- For rehires: original hire may differ from current hire (affects seniority/PTO accrual)

**🔴🔴🔴 EXAMPLE IT0041 DATA (minimum 2 rows per employee):**
| 00000001 | 01 | 2027-01-01 | 9999-12-31 | 2027-01-01 |
| 00000001 | 03 | 2027-01-01 | 9999-12-31 | 2027-01-01 |
**Every employee MUST have at least 2 IT0041 rows (SUBTY=01 Original Hire + SUBTY=03 Seniority).**

### IT0105 — Communication
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | SUBTY | Communication Type | R | 0001=Email, 0010=Work Phone |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | USRID_LONG | Communication ID | R | Email address (for SUBTY=0001) or phone (for SUBTY=0010) |

**ONE ROW per communication type per employee** — typically 1-2 rows (email + phone). Email is critical for ESS/MSS payslip distribution.

### IT0014 — Recurring Deductions/Payments
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | SUBTY | Subtype (Wage Type) | R | 4-digit WT from config Tab 7 (2100, 2110, 2120, 2130, 2140, 2150) |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | BETRG | Amount | R | Per-period dollar amount |
| F | ANCUR | Currency | R | USD |
| G | PRETAX | Pre/Post Tax Flag | R | PRE or POST (determines tax treatment) |

**ONE ROW PER DEDUCTION PER EMPLOYEE.**

**If Benefits Approach = Full SAP Benefits**: Typical employee = 3-4 IT0014 rows (non-benefit deductions only):
- WT 2130 FSA/HSA (if not in IT0171), WT 2150 Union Dues (union only), other voluntary deductions
- Benefit plan enrollments are in IT0167-0171, NOT in IT0014

**If Benefits Approach = Deductions Only (IT0014)**: Typical employee = 6-10 IT0014 rows (ALL benefits as deductions):
- WT 2100 Medical premium (pre-tax, IRC §125)
- WT 2110 Dental premium (pre-tax, IRC §125)
- WT 2115 Vision premium (pre-tax, IRC §125)
- WT 2120 401(k) deferral (pre-tax, IRC §401(k))
- WT 2121 Roth 401(k) (post-tax, Roth)
- WT 2130 Medical FSA (pre-tax, IRC §125)
- WT 2131 HSA contribution (pre-tax, IRC §223)
- WT 2140 Basic Life EE portion (post-tax if any)
- WT 2150 Union Dues (post-tax, union only)
- For 401k: BETRG = per-period dollar amount calculated from salary × contribution %
- **CRITICAL**: When using deductions-only approach, IT0014 IS the benefits carrier. Ensure every benefit the employee is enrolled in has a corresponding IT0014 row. Missing rows = missing deductions = incorrect net pay.

**If Benefits Approach = Hybrid**: IT0014 has deduction rows for externally-managed benefits (health/dental/vision) + IT0169 has 401k enrollment. Typical = 4-6 IT0014 rows + 1 IT0169 row.

**🔴🔴🔴 EXAMPLE IT0014 DATA (minimum 3 rows per employee):**
| 00000001 | 2100 | 2027-01-01 | 9999-12-31 | 250.00 | USD | PRE |
| 00000001 | 2120 | 2027-01-01 | 9999-12-31 | 500.00 | USD | PRE |
| 00000001 | 2110 | 2027-01-01 | 9999-12-31 | 45.00 | USD | PRE |
**Each employee MUST have at least 3 IT0014 rows (Medical + 401k + Dental minimum).**

### IT0207 — Residence Tax Area
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Start Date | R | YYYY-MM-DD |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | TXJCD | Tax Jurisdiction Code | R | BSI geocode format: SS-CCC-CCCC. Federal = "00-000-0000". States use SS-CCC-CCCC from config Tab 11. NEVER use text codes like "FED" or state abbreviations. |
| E | TAXAUTH | Tax Authority Description | R | Descriptive label (e.g., "Federal", "WA State", "CA SDI", "TriMet Transit") |
| F | STATE | State Code | R | 2-letter code matching IT0006 REGIO. For Federal row: "FD" |
| G | LOCALITY | Locality | O | City/county code — only if local taxes apply |

**MULTIPLE ROWS per employee (minimum 2):**
- Row 1: Federal tax jurisdiction (TXJCD = "00-000-0000", STATE = "FD")
- Row 2: State income tax (TXJCD = state geocode, STATE = 2-letter code)
- Row 3+: Local/transit tax (if applicable: TriMet, NYC, OH cities)
- Row 4+: SDI/PFL (CA-SDI, NY-PFL, WA-PFML, etc.)
- WA employees: Still need rows for WA-PFML and WA-CARES even though no income tax
- **CRITICAL: Every employee MUST have at minimum a Federal row + state row**

**🔴🔴🔴 EXAMPLE IT0207 DATA (copy this exact pattern for every employee):**
| 00000001 | 2027-01-01 | 9999-12-31 | 00-000-0000 | Federal | FD | |
| 00000001 | 2027-01-01 | 9999-12-31 | 48-201-0000 | WA State | WA | |
**The TXJCD column MUST use XX-XXX-XXXX format. NEVER use "FED", "Federal", or state abbreviations as geocodes.**

### IT0208 — Work Tax Area
Same column structure as IT0207, but for WORK LOCATION (not residence):
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Start Date | R | YYYY-MM-DD |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | TXJCD | Tax Jurisdiction Code | R | BSI geocode for work location. Federal = "00-000-0000". States use SS-CCC-CCCC. NEVER use text codes like "FED". |
| E | TAXAUTH | Tax Authority Description | R | Descriptive label |
| F | STATE | State Code | R | Work state (may differ from IT0207). For Federal row: "FD" |
| G | TAXPC | Work Tax Percentage | R | 100 = full-time at this location |

For multi-state workers: IT0208 work state ≠ IT0207 residence state.
**CRITICAL: Same row structure as IT0207 — Federal row + state row minimum per employee.**

### IT0210 — Tax Withholding (W-4)
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | SUBTY | Subtype | R | 01 = Federal, 02 = State (one per state) |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | TXJCD | Tax Authority Code | R | FED for federal; state BSI code for state |
| F | FILING_STATUS | Filing Status | R | S = Single, MFJ = Married Filing Jointly, HOH = Head of Household |
| G | MULT_JOBS | Step 2(c) Multiple Jobs | R | Y/N (2020+ W-4 checkbox) |
| H | STEP3 | Step 3 Dependents Amount | R | Dollar amount for dependent credits |
| I | STEP4A | Step 4(a) Other Income | R | 0.00 or amount |
| J | STEP4B | Step 4(b) Deductions | R | 0.00 or amount exceeding standard deduction |
| K | STEP4C | Step 4(c) Extra Withholding | R | Additional per-period withholding |
| L | EXEMPT | Exempt | R | N = Not exempt, Y = Exempt from withholding |

**SEPARATE ROW per tax authority. EVERY employee MUST have minimum 2 rows:**
- Row 1: SUBTY=01, Federal W-4 data (REQUIRED for ALL employees)
- Row 2: SUBTY=02, State withholding (REQUIRED for ALL employees, even no-income-tax states like WA — use for PFML/WA Cares withholding elections)
- Row 3+: Additional states if multi-state worker
- **CRITICAL: Do NOT skip state rows for WA/TX/FL employees** — they still need a state row for SUI, PFML, and other state withholding programs

### IT0167 — Health Plans
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BTEFN | Benefit Plan | R | Plan code from config Tab 17 (MED1, MED2, DEN1, VIS1, UHW1) |
| C | BEGDA | Start Date | R | YYYY-MM-DD (plan effective date) |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | COVLV | Coverage Option/Tier | R | EE, EE+SP, EE+CH, FAM |
| F | CSTEE | EE Cost per Period | R | Dollar amount per pay period |
| G | CSTER | ER Cost per Period | R | Dollar amount per pay period |

**ONE ROW PER PLAN per employee** — medical + dental + vision = 3 rows minimum.
- Union employees: Plan = UHW (Union H&W trust) instead of MED/DEN/VIS. ER cost = hourly rate × expected hours. EE cost = 0.
- Temp employees (T1): May not be eligible — omit rows or mark eligibility exception.

### IT0168 — Insurance Plans
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BTEFN | Benefit Plan | R | Plan code from config Tab 17 (LIFE, SUPL, STD1, LTD1) |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | COVAMT | Coverage Amount | R | Life: salary × multiplier. STD/LTD: weekly/monthly benefit |
| F | CSTEE | EE Cost per Period | R | 0 if ER-paid (basic life), $ amount if voluntary |
| G | CSTER | ER Cost per Period | R | ER cost (for basic life, STD, LTD) |
| H | IMPUTED | Imputed Income Flag | O | Y if GTL >$50K (triggers IRS Table I calc) |

**ONE ROW PER PLAN** — basic life + STD + LTD = 3 rows. Optional: supplemental life, AD&D.

### IT0169 — Savings Plans (401k)
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BTEFN | Benefit Plan | R | Plan code from config Tab 17 (401K, ROTH) |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | EEPCT | EE Contribution % | R | 3%-10% (vary across employees) |
| F | EELMT | IRS Annual Limit | R | $23,500 (2025) |
| G | CATCHUP | Catch-Up Eligible | R | Y if age 50+, N otherwise |
| H | ERMATCH | ER Match Description | O | e.g., "100% first 3%, 50% next 2%" |

One row per plan. Auto-enroll at 6% for new hires. Catch-up: $7,500 for 50+, $11,250 for 60-63.

### IT0171 — General Benefits (FSA/HSA)
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BTEFN | Benefit Plan | R | Plan code from config Tab 17 (MFSA, DFSA, HSA1) |
| C | BEGDA | Start Date | R | YYYY-MM-DD |
| D | ENDDA | End Date | R | 9999-12-31 |
| E | ELAMT | Annual Election Amount | R | Employee's elected annual amount |
| F | ANLMT | IRS Annual Limit | R | Medical FSA $3,300, DCFSA $5,000, HSA $4,300/$8,550 |
| G | ERAMT | ER Contribution | O | HSA employer seed (e.g., $500 EE-only, $1,000 family) |

One row per plan. HSA only for HDHP enrollees. FSA not allowed with HSA.

### IT0027 — Cost Distribution (Concurrent Employment / Multi-Cost-Center Only)
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Start Date | R | YYYY-MM-DD |
| C | ENDDA | End Date | R | 9999-12-31 |
| D | KOSTL | Cost Center | R | Cost center code receiving allocation |
| E | PROZN | Percentage | R | Allocation percentage (all rows for one employee must sum to 100%) |
| F | BUKRS | Company Code | R | Must match IT0001 |
| G | GSBER | Business Area | O | Business area code if applicable |

**MULTIPLE ROWS per employee** — one row per cost center allocation. Only generate this sheet if concurrent employment is configured or if employees are allocated across multiple cost centers (e.g., an employee splitting time 60% Engineering / 40% R&D).

### IT0194 — Garnishment Order
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | SUBTY | Garnishment Type | R | CS = Child Support, TL = Tax Levy, SL = Student Loan, CR = Creditor |
| C | BEGDA | Start Date | R | YYYY-MM-DD (court order date) |
| D | ENDDA | End Date | R | 9999-12-31 or specific end date |
| E | BETRG | Amount/Percentage | R | Dollar amount or % of disposable income |
| F | ISSUING_AUTH | Issuing Authority | R | Court/agency name |
| G | CASE_NO | Case Number | R | Court case identifier |
| H | PAYEE | Payee Name | R | State SDU, IRS, creditor name |
| I | PRIORITY | CCPA Priority | R | 1 = Child Support, 2 = Tax Levy, 3 = Student Loan, 4 = Creditor |

Only for garnishment test employees (1-2 employees typically).

### IT0559 — Tax YTD Balances (Mid-Year Go-Live)
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | BEGDA | Period Begin Date | R | YYYY-MM-DD (e.g., 2027-01-01) |
| C | ENDDA | Period End Date | R | YYYY-MM-DD (e.g., 2027-06-30 for Jul go-live) |
| D | TXJCD | Tax Authority Code | R | FED, state BSI code |
| E | TAXTP | Tax Type | R | FIT, SIT, FICA-SS, FICA-MED, FUTA, SUTA, SDI, PFML |
| F | CUMGRS | YTD Taxable Gross | R | Dollar amount (must be mathematically consistent) |
| G | CUMTAX | YTD Tax Withheld | R | Dollar amount (withheld ≈ rate × gross) |

**MULTIPLE ROWS per mid-year employee** (minimum 6 rows):
- Row 1: FIT (Federal Income Tax) — gross × ~15-22% effective rate
- Row 2: FICA-SS (Social Security) — gross × 6.2% up to $176,100 wage base
- Row 3: FICA-MED (Medicare) — gross × 1.45% (+ 0.9% Additional Medicare if >$200K)
- Row 4: SIT (State Income Tax) — varies by state (skip for WA)
- Row 5: FUTA (Federal Unemployment) — ER side, $7,000 wage base × 0.6%
- Row 6: SUTA (State Unemployment) — ER side, state-specific wage base and rate
- Additional: SDI (CA), PFML (WA/OR), transit tax (OR)

### IT2006 — Absence Quotas
| # | SAP Field | Description | R/O | Values/Rules |
|---|-----------|-------------|-----|-------------|
| A | PERNR | Personnel Number | R | |
| B | KTART | Absence/Quota Type | R | From config Tab 12 (VACA, SICK, FMLA, etc.) |
| C | BEGDA | Quota Start Date | R | YYYY-MM-DD (accrual period start) |
| D | ENDDA | Quota End Date | R | YYYY-MM-DD (accrual period end, usually 12/31) |
| E | ANZHL | Entitlement (Hours) | R | Based on accrual tier (80, 120, 160, 200 hrs) |
| F | KVERB | Used/Consumed (Hours) | R | 0 at go-live |
| G | RESTO | Remaining (Hours) | R | = Entitlement - Used |

**ONE ROW PER ABSENCE TYPE PER EMPLOYEE** — PTO + Sick = 2 rows minimum.
- CA employees: Add CA-SICK row (40 hrs). All employees: Add state-mandated sick where applicable.
- Union employees: PTO per CBA, not company policy.
- Part-time: Pro-rate entitlement by EMPCT from IT0007.

## Generation Strategy

**CRITICAL: ALL generated infotype sheets MUST contain data rows. Do NOT create empty placeholder sheets. Only generate sheets that apply to the chosen approach (see Approach-Driven Migration Scope above).**

This file has 18-22 sheets depending on approach. Use a **two-pass generation approach** if the script gets too long:

### Pass 1: Core Infotypes (IT0000-IT0014 + IT0041 + IT0105)
Generate the org/personal/pay infotypes first — these are the most critical:
- IT0000 Actions: 1 row per employee
- IT0001 Org Assignment: 1 row per employee
- IT0002 Personal Data: 1 row per employee (MUST include SINID/SSN)
- IT0003 Payroll Status: 1 row per employee
- IT0006 Addresses: 1 row per employee
- IT0007 Planned Working Time: 1 row per employee
- IT0008 Basic Pay: 1 row per employee
- IT0009 Bank Details: 1 row per employee
- IT0014 Recurring Deductions: **3-10 rows per employee** (depends on benefits approach — 3-4 if full SAP benefits, 6-10 if deductions-only)
- IT0041 Date Specifications: **2-3 rows per employee** (hire date, seniority, benefits eligibility)
- IT0105 Communication: **1-2 rows per employee** (email, phone)

### Pass 2: Tax & Benefits Infotypes (IT0207-IT2006)
Then add tax areas, withholding, benefits, and special infotypes:
- IT0207 Residence Tax: **2+ rows per employee** (Federal + state)
- IT0208 Work Tax: **2+ rows per employee** (Federal + state)
- IT0210 Withholding: **2+ rows per employee** (Federal + state)
- IT0167 Health Plans: **2-3 rows per employee** (medical + dental + vision) — **SKIP if Deductions-Only approach**
- IT0168 Insurance: **2-3 rows per employee** (life + STD + LTD) — **SKIP if Deductions-Only approach**
- IT0169 Savings: 1 row per eligible employee (401k) — **SKIP if Deductions-Only approach**
- IT0171 General Benefits: 1 row per eligible employee (FSA/HSA) — **SKIP if Deductions-Only approach**
- IT0027 Cost Distribution: 2+ rows per multi-cost-center employee — **Only if concurrent employment**
- IT0194 Garnishment: Only for garnishment test employees
- IT0559 Tax YTD: Only for mid-year hires (4-6 rows per employee) — **Only if mid-year go-live**
- IT2006 Absence Quotas: **2+ rows per employee** (PTO + sick)

**If the script is too long, split into two sequential scripts** — the second opens the file and adds remaining sheets. But NEVER save with empty sheets.

### Completeness Check
After generating, verify EVERY infotype sheet has the expected number of rows. A 15-employee migration file should have ~350-500 total data rows across all sheets.

## Output Format

Generate .xlsx using Python openpyxl with 18 infotype sheets plus a Cover/Index sheet.

Format requirements:
- **Cover/Index tab**: Project info, loading order instructions, employee roster summary, record counts per sheet
- Professional styling: navy header row (#1F4E79, white text, bold), thin gray borders
- Light green fill (#E8F5E9) on cells with values derived from config workbook (for traceability)
- Light yellow fill (#FFFFF0) on cells requiring manual input or client confirmation
- Red fill on any cell marked "PLACEHOLDER" or "TBD"
- Auto-filters on all data sheets
- Freeze panes at row 4
- Row 1: Sheet title with infotype number (merged, 14pt bold)
- Row 2: SAP infotype description and LSMW object reference (merged, 10pt italic)
- Row 3: Column headers (navy fill, white text, bold, wrapped)
- Row 4+: Employee data rows
- Arial 10pt throughout
- Data validation: dropdowns for EE Group, EE Subgroup, filing status, Y/N fields
- Column widths optimized for readability

### Cover Sheet Content
Include on the cover sheet:
1. Document title: "SAP HCM Payroll — Hiring Data Migration File"
2. Company name (from config workbook)
3. Generated date
4. Config workbook source reference
5. **Employee Roster**: Table listing all employees with PERNR, Name, EE Group, EE Subgroup, PA, PSA, Payroll Area, State, Scenario Type
6. **Loading Order**: Numbered list of infotypes in dependency order with record counts
7. **Validation Checklist**: Pre-load checks (e.g., "Verify all PA codes exist in SAP", "Verify all tax authorities are configured in BSI")
8. **Color Legend**: Green = from config workbook, Yellow = requires manual input, Red = placeholder/TBD

Save to workspace outputs as `SAP_Payroll_MigrationFile_[CompanyName].xlsx`.

## Post-Generation Validation

After generating, perform these validation checks and report results:
1. **Cross-reference check**: Every org code (PA, PSA, EE Group, Subgroup) used in IT0001 exists in config workbook Tab 1
2. **Wage type check**: Every WT in IT0008/IT0014 exists in config workbook Tab 5
3. **Tax authority check**: Every authority in IT0207/0208/0210 exists in config workbook Tab 8
4. **Benefit plan check**: Every plan in IT0167-0171 exists in config workbook Tab 14
5. **WSR check**: Every work schedule rule in IT0007 exists in config workbook Tab 4
6. **Consistency check**: IT0006 state matches IT0207 state for each employee
7. **Completeness check**: Every configured state has at least one employee
8. **Garnishment check**: Garnishment types in IT0194 match config workbook Tab 11

Report validation results as a summary after file generation.

## Output Self-Validation (LLM QA Gate)

**After generating the .xlsx AND running the cross-reference checks above, perform an LLM-powered deep validation.** This is the final quality gate before the migration file is delivered.

### Step 1: Programmatic Validation Script
Write and execute a Python validation script that opens the generated .xlsx and checks:

```
MIGRATION FILE VALIDATION CHECKLIST:
□ Core infotypes present: IT0000, IT0001, IT0002, IT0003, IT0006, IT0007, IT0008, IT0009, IT0014
□ New infotypes present: IT0041 (Date Specifications), IT0105 (Communication)
□ Tax infotypes present: IT0207, IT0208, IT0210
□ Benefits infotypes present: IT0167, IT0168, IT0169, IT0171 (ONLY if Full/Hybrid Benefits approach)
□ If Deductions-Only approach: IT0167-IT0171 should NOT exist; IT0014 avg rows >= 6 per employee
□ If Concurrent Employment: IT0027 (Cost Distribution) present
□ Special infotypes: IT0194 (if garnishments), IT0559 (if mid-year), IT2006
□ Employee count >= 10 across all IT sheets
□ NO empty infotype sheets (every generated IT sheet has data rows)
□ Cover/Summary sheet present
□ Data Quality Review sheet present with AI findings
□ NO "ESSION" pattern fields in any cell
□ NO "FED" text in TXJCD columns (must be "00-000-0000")
□ Federal geocode "00-000-0000" exists in IT0207 and IT0208
□ IT0210: average >= 2 rows per employee
□ IT0014: average >= 2 deductions per employee (>= 6 if Deductions-Only approach)
□ IT0002 SSNs all start with "9" (900-series test data)
□ IT0041: at least 2 rows per employee (hire date + seniority date)
□ IT0105: at least 1 row per employee (email address)
□ All configured states represented in IT0006/IT0207/IT0208
□ All PA codes from config workbook used in IT0001
□ All payroll areas from config workbook used in IT0001
□ Benefits approach consistency: if config Tab 17 = "Deductions Only", IT0167-0171 must NOT exist
```

### Step 2: LLM Data Quality Review
Pass a structured summary of the migration data to the AI (employee roster, sample rows from each IT) and verify:

1. **Salary reasonableness by role**:
   - Executives: $150K+ annual (not $30K)
   - Salaried professionals: $60K-$150K (industry-appropriate)
   - Hourly workers: $15-$45/hr (not $5 or $500)
   - Part-time: pro-rated correctly
   - Interns: $20-$30/hr or stipend

2. **Tax area consistency**:
   - IT0207 (residence) state matches IT0006 (address) state for each PERNR
   - IT0208 (work) state matches the PA's assigned state
   - Multi-state workers correctly have different IT0207 vs IT0208 states

3. **Benefits eligibility logic**:
   - Part-time / temp employees should NOT have full-time-only benefits
   - Union employees should have union-specific benefit plans
   - Executives should have enhanced benefits (higher life coverage, etc.)

4. **Deduction limits compliance**:
   - 401(k) annual max: $23,500 (per-period = annual ÷ pay periods)
   - FSA annual max: $3,300
   - HSA annual max: $4,300 (self) / $8,550 (family)
   - Catch-up 401(k): $7,500 for 50+, $11,250 for 60-63

5. **Employee scenario diversity**:
   - At least 1 employee per configured state
   - At least 1 employee per EE subgroup
   - At least 1 employee per payroll area
   - Multi-state worker scenario (if >1 state)
   - Garnishment recipient (if garnishments configured)
   - Mid-year hire (if mid-year go-live)

6. **Date consistency**:
   - BEGDA dates are realistic (not in the past for new system)
   - ENDDA = 9999-12-31 for active records
   - IT0559 YTD dates align with go-live date

### Step 3: Generate Data Quality Review Sheet
Insert the LLM's findings as a **"Data_Quality_Review"** sheet in the migration file itself with these columns:
| Finding ID | Severity | Employee (PERNR) | Infotype | Issue | Resolution | Status |

Severity levels:
- **CRITICAL**: Blocks LSMW import or causes payroll error
- **WARNING**: May cause incorrect payroll calculation
- **INFO**: Best practice recommendation

### Step 4: Auto-Fix and Report
- If any infotype sheet is empty, **GENERATE DATA** for it
- If "FED" text appears in TXJCD, **REPLACE** with "00-000-0000"
- If salary values are unreasonable, **ADJUST** to industry norms
- If Data Quality Review sheet is missing, **ADD** it with findings
- If SSNs don't start with 9, **REPLACE** with 900-series

After all fixes, generate and print a **validation scorecard**:
```
══════════════════════════════════════════════
  MIGRATION FILE VALIDATION SCORECARD
══════════════════════════════════════════════
  Infotype sheets:    XX / 18
  Total data rows:    XXX
  Employees:          XX
  Structural checks:  XX / XX passed
  ESSION scan:        CLEAN
  BSI geocode format: PASS / FAIL
  Cross-ref to config: XX / 8 checks passed
  Data Quality Review: XX findings (C:X W:Y I:Z)
  LLM salary review:  PASS / X adjustments
  LLM tax consistency: PASS / X issues
  LLM benefits logic:  PASS / X issues
  ──────────────────────────────────────────
  OVERALL:            PASS / FAIL
══════════════════════════════════════════════
```

**If OVERALL = FAIL, fix the issues and re-validate before presenting to user.**
**Always report the scorecard to the user when presenting the output.**
