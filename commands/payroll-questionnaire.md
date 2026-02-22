---
description: Generate blank SAP payroll discovery questionnaire
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, TodoWrite
argument-hint: [company-name]
---

Generate a blank SAP HCM Payroll Discovery Questionnaire template as a professional .docx file. This template is designed for a payroll consultant to fill out during client discovery sessions.

Read the skill file at `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/SKILL.md` first to understand the implementation framework. Then read relevant reference files from `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/references/` to ensure the questionnaire covers all required SAP configuration areas.

## What to Generate

A professional .docx questionnaire template with **blank response fields** that a consultant will complete during discovery sessions with the client. Use placeholder text like "[Enter company name]", "[List all states]", "[Specify pay frequency]" in response columns.

If `$ARGUMENTS` is provided, pre-fill the company name throughout the document. Otherwise use "[Company Name]" as placeholder.

Use AskUserQuestion to ask:
1. Should the questionnaire include pre-filled example guidance in each response cell (helps junior consultants), or leave responses completely blank?
2. Are there any sections the consultant wants to skip or add?
3. What industry is the company in? (Manufacturing, Healthcare, Retail, Technology, Construction, Financial Services, Other)

## AI-Powered Industry Profiling

After gathering company details, use the LLM to generate **industry-specific customization**:

### Step 1: Industry Analysis
Call the AI to analyze the company's industry and generate:
- **Industry Guidance Insert** (1-2 pages): A pre-filled guidance section at the beginning of the questionnaire explaining common payroll complexities for this specific industry. For example:
  - Manufacturing → prevailing wage, shift rotation patterns, hazard pay, piece rate, Davis-Bacon
  - Healthcare → on-call/callback pay, PRN/per diem rates, credential premiums, 12-hour shifts
  - Retail/Hospitality → tip credit/wages, split shift premium, seasonal workers, minimum wage compliance
  - Technology → RSU/stock option reporting, global mobility, remote work tax nexus, highly compensated employees
  - Construction → certified payroll, multi-state job costing, union fringe, Davis-Bacon
  - Financial Services → deferred compensation, clawback provisions, FINRA requirements

### Step 2: Industry-Specific Questions
Call the AI to generate 5-8 **additional industry-specific questions** that get inserted into the relevant sections. These are questions that a generic questionnaire would miss but are critical for this industry. Insert them into the appropriate sections with a marker: "🔹 Industry-Specific Question".

### Step 3: State-Specific Alerts
Based on the states provided, call the AI to generate **state compliance alerts** — brief notes inserted into the questionnaire highlighting state-specific requirements the consultant must probe:
- CA: daily OT, meal/rest break penalties, CA-SDI, paid sick leave
- NY: NYC wage theft prevention act, NY PFL, NYC local tax
- WA: WA Cares Fund, PFML, no state income tax
- IL: flat 4.95% tax, IL PFML (coming), Chicago fair workweek
- etc.

The AI-generated content should be clearly marked with a header: "📋 AI-Generated Industry Guidance" so the consultant knows it was auto-generated and should be verified.

## Questionnaire Structure (15 Sections)

Generate a .docx using the docx npm package (docx-js) with question-and-response tables for each section:

**Section 1: Company Overview** — Legal entity name, DBA, EIN, industry/NAICS, headquarters, total headcount, states of operation, union status, current payroll system, target go-live, SAP landscape, other SAP modules live, project approach

**Section 1A: Implementation Approach Decisions** — These are CRITICAL architectural decisions that shape the entire downstream pipeline. Ask ALL of these:

| Decision | Options | Impact |
|----------|---------|--------|
| **Time Management Approach** | (A) Full SAP Time Evaluation (PT60/RPTIME00 — positive time recording with CATS or time clocks), (B) Negative Time Only (SAP handles absences only; planned time = actual time unless absence recorded), (C) 3rd-Party Time Import (time data from Kronos/ADP/Ceridian feeds into SAP via IT2010/IT2012 or custom interface — SAP does NOT do time evaluation) | Determines whether Tab 12 (Absence/Quota) is full config vs minimal, whether time evaluation schemas are needed, and whether a time interface is required |
| **Benefits Approach** | (A) Full SAP Benefits Module (PA-BN — IT0167/0168/0169/0171 with plans, eligibility rules, open enrollment in SAP), (B) Deductions Only via IT0014 (benefit deductions loaded as recurring payments — no plan enrollment in SAP, benefits administered in external system like Workday/BenefitFocus/ADP), (C) Hybrid (health/dental/vision in external system as IT0014 deductions; 401k managed in SAP IT0169) | Determines whether Tabs 17 (Benefits Config) and migration IT0167-0171 sheets are full vs. stub, and whether benefits carrier interfaces are needed |
| **Organizational Management Scope** | (A) Full OM (positions, org units, jobs, reporting hierarchy in SAP — separate PA-OM project), (B) Minimal OM (org units and positions created for IT0001 assignment only — no full hierarchy), (C) No OM (IT0001 uses cost centers and free-text org assignment — no position management) | Determines whether OM objects appear in migration file and whether ORGEH/PLANS/STELL fields in IT0001 are populated or left blank |
| **Go-Live Timing** | (A) January 1 (clean year — no YTD migration needed), (B) Mid-Year (requires IT0559/IT0560 YTD balance migration from legacy system) | Determines IT0559 migration scope and parallel run requirements |
| **Concurrent Employment** | (A) Yes — employees can hold multiple positions simultaneously (healthcare, education, retail), (B) No — standard single employment | Determines whether IT0000-IT0001 need concurrent employment action types and whether cost distribution (IT0027) is critical |

**Section 2: Enterprise Structure** — Company code(s), chart of accounts, fiscal year variant, currency, personnel areas (one per location), personnel subareas, employee groups, employee subgroups with FLSA status

**Section 3: Payroll Areas & Processing** — Payroll areas by frequency, pay day rules, PCC usage, simulation/correction/live run schedule, retroactive accounting depth, payroll lock timing

**Section 4: Compensation & Wage Types** — Regular earnings (salary, hourly, OT, DT, shift diff, holiday premium), leave/absence earnings (PTO, sick, bereavement, jury duty, FMLA), supplemental earnings (bonus, commission, relocation, severance, tuition, referral), statutory deductions (federal, state, local, FICA), voluntary deductions (medical, dental, vision, 401k, FSA, life, union dues), employer contributions (ER FICA, FUTA, SUTA, ER medical/dental/vision, ER 401k match, ER life/STD/LTD)

**Section 5: Tax Configuration** — Tax calculation engine (BSI version), tax filing service, W-4 version (2020+ format), resident tax policy, reciprocity agreements, multi-state workers (allocation method, de minimis thresholds), supplemental tax method (flat 22% or aggregate), state-by-state tax summary including: income tax Y/N, SUI wage base, SDI/PFL/TDI, local taxes (NYC, Philadelphia, OH cities), mandatory EE contributions (WA Cares, MA PFML, etc.), tax deposit schedule (semi-weekly/monthly)

**Section 6: Time Management** — **Adapt this section based on Section 1A Time Management Approach:**

- **If Approach (A) Full Time Eval**: Time recording method by employee type, time source system (CATS, time clocks, ESS), time evaluation schema (TM04 or custom), time types (T555A), time wage types, overtime calculation method (specify states with daily OT like CA/CO/AK), rounding rules, absence types with paid/unpaid/accrual rules, PTO accrual tiers by tenure, state-mandated sick leave, shift definitions (start/end times, differentials), work schedule rules by employee type, meal/rest break policy by state, time transfer to payroll (IT2010/IT2012)
- **If Approach (B) Negative Time Only**: Work schedule rules (planned hours = actual hours unless absence), absence types with paid/unpaid status, PTO/sick accrual tiers by tenure, state-mandated sick leave, overtime handling (manual entry via IT2005 or IT0015?), holiday pay rules. **Skip**: time evaluation schemas, CATS config, time clocks, rounding rules
- **If Approach (C) 3rd-Party Time Import**: Source system name and version, interface protocol (file/API/IDoc), file layout and frequency, which SAP infotypes receive the data (IT2010 attendances? IT2012 time transfer? IT0015 additional payments?), overtime already calculated by source system (Y/N), absence management still in SAP (Y/N)?, work schedule rules still needed for planned time, reconciliation approach between source system and SAP

**Section 7: Benefits Integration** — **Adapt this section based on Section 1A Benefits Approach:**

- **If Approach (A) Full SAP Benefits**: Health & welfare plans (carrier, tiers, premiums, eligibility waiting period), plan types and subtypes (T5UBP), eligibility rules (T5UB1 — waiting period, FT/PT, EE subgroup), open enrollment setup, retirement plan (type, provider, match formula with tiers, vesting schedule, eligibility criteria, auto-enroll, catch-up), HSA (HDHP required, ER seed contribution), FSA (medical + dependent care limits), insurance (basic life coverage multiplier, supplemental life, AD&D, STD elimination/benefit, LTD elimination/benefit), union-specific benefits (H&W fund, pension, union dues formula), imputed income for GTL >$50K, COBRA administration, benefits carrier interfaces
- **If Approach (B) Deductions Only via IT0014**: List each benefit deduction with: wage type code, pre/post tax treatment, per-period amount or percentage, IRC section (125/401k/Roth/129/223), IRS annual limits, which employees are eligible. **No SAP benefit plans are configured** — IT0167-0171 are NOT used. All benefit enrollment is managed in external system. Only IT0014 recurring deductions carry the dollar amounts into payroll. Still need: imputed income for GTL >$50K (can be IT0015 additional payment or custom wage type)
- **If Approach (C) Hybrid**: Which benefits are in SAP (typically 401k via IT0169) vs. external (typically health/dental/vision as IT0014 deductions). For SAP-managed plans: full plan config. For external: deduction-only approach per (B)

**Section 8: Garnishments** — SAP infotypes used, priority ordering, disposable income rules, garnishment types (child support, tax levy, student loan, creditor, bankruptcy), multi-garnishment handling, remittance method, state-specific rules

**Section 9: Off-Cycle Payroll** — Scenarios (terminations, corrections, bonuses, check replacement), state-mandated final pay timelines, PTO payout policy, off-cycle tax method, PCC off-cycle process

**Section 10: Interfaces & Integration** — Outbound (FI posting, bank transfer, positive pay, tax filing, 401k, benefits carriers, workers comp) and inbound (time data, new hire, benefits elections, org changes) with target system, frequency, format, protocol

**Section 11: Reporting Requirements** — Standard SAP reports needed, custom reports needed, frequency, audience

**Section 12: Year-End Processing** — W-2 generation, distribution method, W-2c process, year-end adjustments, BSI update process, payroll year-end close, ACA reporting

**Section 13: Security & Authorization** — Authorization concept, role definitions (payroll admin, manager, HR admin, ESS, MSS, PCC roles), SOX controls

**Section 14: Data Migration & Cutover** — Source system, migration scope, YTD balance approach (IT0559/0560), migration tool, parallel run plan, cutover sequence, reconciliation approach

**Section 15: Sign-Off** — Signature table with Name, Role, Signature, Date columns (pre-filled with typical roles: VP HR, Payroll Manager, CFO, SAP Project Manager, SAP Consultant)

## Format Requirements

- US Letter page size (12240 x 15840 DXA), 1-inch margins
- Arial font throughout, navy headers (#1F4E79)
- Two-column tables: Question/Item (bold, ~35% width) | Response (~65% width, blank or placeholder)
- Multi-column tables for structured data (wage types, absence types, interfaces)
- Response cells should have light gray fill (#F9F9F9) to visually indicate fillable areas
- Table of Contents
- Cover page with: document title, company name placeholder, version, date, status "DRAFT - For Discovery"
- Headers: company name + "SAP HCM Payroll Discovery Questionnaire"
- Footers: "DRAFT - Confidential" + page numbers
- Validate with the docx validation script after generation

Save to the workspace outputs folder as `SAP_Payroll_Questionnaire_[CompanyName].docx` (or `SAP_Payroll_Questionnaire_Template.docx` if no company specified).

## Output Self-Validation (LLM QA Gate)

**After generating the .docx file, perform an LLM-powered self-validation before presenting it to the user.** This is a mandatory quality gate — do NOT skip it.

### Step 1: Structural Verification
Read the generated .docx back and verify:
- All 15 sections are present and have question tables
- Each section has at least the minimum number of questions:
  - Section 1 (Company Overview): 8+ questions
  - Section 2 (Enterprise Structure): 6+ questions
  - Section 3 (Payroll Areas): 5+ questions
  - Section 4 (Compensation & Wage Types): 10+ questions
  - Section 5 (Tax Configuration): 8+ questions
  - Section 6 (Time Management): 7+ questions
  - Section 7 (Benefits): 8+ questions
  - Section 8 (Garnishments): 4+ questions
  - Section 9 (Off-Cycle): 4+ questions
  - Section 10 (Interfaces): 5+ questions
  - Section 11 (Reporting): 3+ questions
  - Section 12 (Year-End): 4+ questions
  - Section 13 (Security): 3+ questions
  - Section 14 (Data Migration): 5+ questions
  - Section 15 (Sign-Off): signature table present
- Industry-specific questions are included (if industry was specified)
- State compliance alerts are included (if states were specified)
- Cover page, TOC, headers, and footers are present

### Step 2: LLM Semantic Review
Pass the full generated questionnaire content to the AI and ask it to evaluate:
1. **Coverage completeness**: Are there any critical SAP payroll topics that are NOT covered by the questions? (Check against the full SAP HCM payroll implementation checklist)
2. **Question clarity**: Are any questions ambiguous or too vague to yield actionable configuration data?
3. **Industry alignment**: Do the industry-specific additions actually match the stated industry?
4. **Downstream readiness**: Will the answers to these questions be sufficient to generate a complete functional spec?
5. **Missing edge cases**: Are there common client scenarios not addressed? (e.g., multi-state workers, mid-year go-live, complex garnishments)

### Step 3: Auto-Fix and Report
- If any structural issues are found, FIX THEM in the .docx before saving
- If LLM finds missing questions, ADD THEM to the appropriate section
- After fixes, append a **"📋 QA Validation Summary"** section at the end of the document:
  - Sections validated: X/15
  - Total questions: N
  - Industry-specific additions: N
  - LLM review: PASS / PASS WITH NOTES / issues found
  - Any items the LLM flagged for human review

**Report the validation summary to the user when presenting the output.**
