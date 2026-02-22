---
description: Generate functional spec from completed questionnaire
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, TodoWrite
argument-hint: <questionnaire.docx>
---

Generate a SAP HCM Payroll Functional Specification from a completed Payroll Discovery Questionnaire.

**The questionnaire is the single source of truth.** Every design decision in the functional spec must trace back to a specific questionnaire response.

Read the skill file at `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/SKILL.md` first. Then read ALL reference files from `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/references/` to translate business requirements into SAP functional design.

## Input

The user must provide a completed questionnaire .docx file (via upload or file path). If no file is provided, ask the user to upload or specify the path.

Read and parse the entire questionnaire to extract all company-specific responses. These responses drive every section of the functional spec.

## Questionnaire-to-FuncSpec Mapping

Transform each questionnaire section into SAP functional design:

| Questionnaire Section | Functional Spec Output |
|---|---|
| Q1: Company Overview | FS1: Document Control & Scope |
| Q2: Enterprise Structure | FS2: Enterprise Structure Design (PA/PSA matrix, EE Group/Subgroup, holiday calendars, WSR) |
| Q3: Payroll Areas | FS3: Payroll Area Configuration (V_T549A params, PCC setup) |
| Q4: Wage Types | FS4: Wage Type Catalog (full catalog with processing/evaluation classes) |
| Q5: Tax Config | FS5: Tax Configuration Design (authorities, IT0210, BSI, multi-state) |
| Q6: Time Mgmt | FS6: Time-to-Payroll Integration (data flow, absence valuation, OT rules) |
| Q7: Benefits | FS7: Benefits Integration Design (plans, eligibility, match formulas, imputed income) |
| Q8: Garnishments | FS8: Garnishment Processing Design (priority, disposable income, states) |
| Q9: Off-Cycle | FS3.2: PCC Off-Cycle Configuration |
| Q10: Interfaces | FS10: Interface Specifications (all inbound/outbound) |
| Q11: Reporting | FS11: Reporting Design |
| Q12: Year-End | FS5.3: Year-End/Tax Filing |
| Q13: Security | Referenced in FS (PCC roles, SOD) |
| Q14: Data Migration | FS12: Data Migration Functional Design |

## Approach-Driven Design

The questionnaire Section 1A captures critical architectural decisions that shape the ENTIRE functional spec. Extract these first and apply them throughout:

### Time Management Approach
- **Full Time Eval** → FS6 is a full time evaluation design (schemas, time types, PCRs for OT). Config workbook gets full Tab 12.
- **Negative Time Only** → FS6 covers only absences and work schedules. No time evaluation schema. OT is entered manually (IT2005 overtime or IT0015 additional payments). Config workbook Tab 12 is absence-only (no time types, no CATS, no time evaluation).
- **3rd-Party Time Import** → FS6 focuses on the inbound time interface spec (file layout, frequency, mapping to SAP wage types). Absences may still be in SAP. Include interface in FS10. Config workbook Tab 12 is minimal (absences only if SAP-managed). Add time import interface to Tab 16.

### Benefits Approach
- **Full SAP Benefits** → FS7 is a full benefits design (plan types, eligibility, IT0167-0171). Config Tab 17 gets full plan configuration.
- **Deductions Only (IT0014)** → FS7 becomes a short "Benefits Deduction Mapping" section listing each benefit deduction wage type, pre/post tax treatment, and IRS limits. NO plan configuration. Config Tab 17 is replaced with a simple deduction reference table. Migration skips IT0167/0168/0169/0171 entirely — all benefits flow through IT0014 rows.
- **Hybrid** → FS7 splits: SAP-managed plans (typically 401k) get full design; external-managed plans (health/dental/vision) get deduction-only treatment via IT0014.

### OM Scope
- **Full OM** → IT0001 ORGEH/PLANS/STELL fields are populated. OM objects are a separate migration scope (not covered by this plugin — note as dependency).
- **Minimal OM** → Basic org units/positions created for IT0001 linkage. Include minimal OM creation in migration.
- **No OM** → IT0001 uses KOSTL (cost center) as primary org assignment. ORGEH/PLANS/STELL left blank or "99999999".

### Concurrent Employment
- **Yes** → Design concurrent employment actions (MASSN=ZC), IT0000/IT0001 support for multiple assignments, cost distribution via IT0027, prorated benefits eligibility.
- **No** → Standard single-employment design.

## Key Translation Rules

When translating questionnaire responses to functional design:

1. **Wage Types**: For each earning/deduction/ER contribution mentioned in Q4, assign: a wage type code (1000-3999 range), model wage type to copy from, source infotype, processing class values (PC01-PC71), evaluation class values (EC01), and cumulation assignment. Use the wage-types.md reference for standard assignments.

2. **Tax Authorities**: For each state in Q5, specify: BSI state code, IT0210 subtype, income tax method, SUI/SDI requirements. Use tax-configuration.md reference for state details.

3. **Work Schedules & OT**: Define work schedule rules per employee type (NORM, SH01-SH03, FLEX, PART). For states with daily OT (CA, CO, AK, NV), specify daily/weekly thresholds and interaction rules. Define shift differential amounts and assignment method. Use work-schedules-ot.md reference for state-specific rules.

4. **Benefits Integration**: For each benefit plan, specify: plan type, eligibility rule, waiting period, EE deduction WT, ER contribution WT, contribution formula (with match tiers for 401k), IRS annual limits, imputed income calculation for GTL >$50K. For union benefits: H&W fund $/hour, pension $/hour per CBA terms. Use benefits-config.md reference.

5. **Schemas/PCRs**: Based on the requirements (CA daily OT, 401k match formula, shift diffs, imputed income, etc.), identify which custom schemas (copy of U000, TM04, UEND) and PCRs are needed. Use schemas-pcrs.md reference. Keep schema detail high-level (function references, not pseudocode).

6. **Symbolic Accounts**: Map each wage type category to a symbolic account and GL account range. Include cost center derivation rules (IT0001 vs IT0027) and posting variant config. Use fi-posting.md reference.

7. **Interfaces**: For each system mentioned in Q10, specify: SAP program, file format, protocol, file naming convention, error handling. Use interfaces.md reference.

8. **Traceability**: Every functional spec section must reference its source questionnaire section (e.g., "Reference: Questionnaire Section 4").

## AI-Powered Design Intelligence

After translating the questionnaire into SAP functional design, use the LLM to enrich the document:

### AI Executive Summary
Call the AI to generate a **300-400 word executive summary** for the beginning of the document:
- Project objective and scope (employees, states, payroll areas)
- Key design decisions and their business impact
- Areas of complexity requiring special attention (e.g., CA daily OT, multi-state, union)
- Dependencies and assumptions
- Recommended implementation timeline considerations

### AI Design Rationale (per section)
For each major funcspec section (FS2-FS10), call the AI to generate a **"Design Rationale" paragraph (150-250 words)** that explains:
- WHY these design decisions were made (not just WHAT they are)
- What SAP best practices are being followed
- What trade-offs or alternatives were considered and rejected
- What risks exist with this design approach

Insert as a gray-boxed callout at the end of each section with header: "📋 Design Rationale"

### AI Complexity & Risk Assessment
Call the AI to generate a **risk assessment table** as a new section at the end:

| Area | Complexity | Risk Level | Est. Config Effort | Key Risk Factors | Test Approach |
|------|-----------|------------|-------------------|-----------------|---------------|

Rate each functional area: Enterprise Structure, Payroll Areas, Wage Types, Tax Config, Work Schedules, Benefits, Garnishments, Schemas/PCRs, FI Posting, Interfaces, Migration.

### AI Cross-Reference Validation
After generating all sections, call the AI to perform a **cross-reference integrity check**:
- Does every wage type referenced in FS4 trace back to a questionnaire response?
- Does every state in FS5 have corresponding WSR rules in FS3 (if applicable)?
- Are all benefit plan WTs in FS7 also defined in the FS4 wage type catalog?
- Flag any "orphaned" references (mentioned but not fully designed)

Insert findings as a "🤖 AI Integrity Check" section at the end of the document.

## Output Format

Generate a professional .docx using docx-js with 14 sections as defined in the mapping above.

Each section must include:
- Reference to source questionnaire section
- SAP table references (V_T511, V_T549A, V_T5UTZ, etc.)
- IMG path references where applicable
- Professional tables with navy headers
- Specific values derived from the questionnaire (not generic templates)

Format requirements:
- US Letter, 1-inch margins, Arial font
- Navy headers (#1F4E79), professional tables
- Table of Contents, headers/footers with page numbers
- Document ID (e.g., [COMPANY]-PAY-FS-001) and version control on cover page
- Validate with docx validation script

Save to workspace outputs as `SAP_Payroll_FuncSpec_[CompanyName].docx`.

## Output Self-Validation (LLM QA Gate)

**After generating the funcspec .docx, perform an LLM-powered self-validation before presenting it to the user.** This is a mandatory quality gate.

### Step 1: Structural Verification
Read the generated funcspec back and verify:
- All 14 functional spec sections (FS1-FS12 + AI sections) are present
- Each section references its source questionnaire section
- SAP table references are included in each design section
- Document has cover page, TOC, version control
- Executive Summary is present
- Risk Assessment table is present
- AI Cross-Reference Validation section is present

### Step 2: SAP Domain Accuracy Check
Pass the funcspec content to the AI and verify:
1. **Wage type code ranges**: Are all assigned codes in valid SAP ranges? (1000-1999 earnings, 2000-2999 deductions, 3000-3999 ER contributions, /1xx-/8xx statutory)
2. **Processing class assignments**: Do PC values follow SAP US payroll standards? (PC01=valuation basis, PC10=tax treatment, PC20=time quotient, PC71=garnishment)
3. **BSI geocode format**: Are all tax jurisdictions in SS-CCC-CCCC format? Federal = 00-000-0000?
4. **SAP table names**: Are all referenced SAP tables/views real? (V_T511, V_T549A, T001P, V_T5UTZ, etc.)
5. **ESSION field check**: Scan for ANY hallucinated field names containing "ESSION" — these are ALWAYS wrong
6. **Feature names**: Are PE03 features valid? (ABKRS, LGMST, SCHKZ, TARIF, PINCH)
7. **Schema/PCR references**: Are referenced schemas based on valid standard schemas? (U000, UEND, TM04, UT00)

### Step 3: Traceability & Completeness
Pass all questionnaire sections alongside the funcspec and have the AI verify:
1. **Forward traceability**: Every questionnaire response maps to a funcspec design decision
2. **No orphan references**: Every funcspec item traces back to a questionnaire response
3. **Wage type completeness**: Count WTs in funcspec vs what was described in questionnaire — are any missing?
4. **State coverage**: Every state mentioned in questionnaire has tax authority design in funcspec
5. **Benefits alignment**: Every benefit plan in questionnaire has integration design in funcspec

### Step 4: Auto-Fix and Report
- If ESSION fields are found, REPLACE with correct SAP field names
- If processing class values seem wrong, CORRECT them
- If any funcspec section is missing its questionnaire traceability reference, ADD it
- Append a **"📋 FuncSpec Validation Summary"** section at the end:
  - Sections generated: X/14
  - Wage types designed: N (target: M from questionnaire)
  - Tax authorities designed: N (target: M states)
  - SAP domain accuracy: PASS / issues corrected
  - ESSION check: CLEAN / corrected N fields
  - Traceability: COMPLETE / gaps found

**Report the validation summary to the user when presenting the output.**

After generating, summarize what was produced and ask if the user wants to proceed to the configuration workbook.
