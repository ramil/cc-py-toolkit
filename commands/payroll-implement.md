---
description: Full pipeline: QA questionnaire then generate all docs
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, TodoWrite
argument-hint: <questionnaire.docx>
---

Run the complete AI-enhanced SAP HCM Payroll Implementation pipeline from a completed questionnaire: QA validation (with AI semantic analysis), Functional Specification (with AI design rationale), Configuration Workbook (with AI conflict detection and smart test scenarios), and Executive Briefing (AI-generated cross-document synthesis).

**The questionnaire is the single source of truth.** This command reads it once and generates all downstream deliverables.

Read the skill file at `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/SKILL.md` first. Then read ALL reference files from `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/references/`.

## Input

The user must provide a completed questionnaire .docx file (via upload or file path). If no file is provided, ask the user to upload or specify the path.

## Pipeline Steps

Use TodoWrite to track progress through all four steps.

### Step 1: Parse Questionnaire
Read and parse the entire questionnaire document. Extract all company-specific responses into a structured understanding of:
- Company name and details
- All personnel areas, subareas, EE groups/subgroups
- All wage types (earnings, deductions, ER contributions)
- Tax jurisdictions and state details
- Time management setup
- Benefits plans and deductions
- Garnishment requirements
- Interface specifications
- Reporting needs
- Migration plan

### Step 2: QA Validation (AI-Enhanced)
Perform the full QA validation as defined in the `/payroll-qa` command, including AI-powered analysis:
- Completeness check (all 15 sections answered)
- Enterprise structure consistency
- Wage type completeness
- Tax configuration validation (every state covered)
- Benefits-payroll alignment
- Time-payroll integration
- Garnishment validation
- Interface completeness
- Cross-section consistency
- Go-live readiness

Generate a QA report (.docx) with AI semantic analysis, contradiction detection, risk narrative, and gap prediction. Present the summary.

**Decision point:**
- If PASS or PASS WITH CONDITIONS: Inform the user of any conditions, then automatically proceed to Step 3.
- If FAIL: Present critical findings and ask user whether to proceed anyway or stop to fix the questionnaire. Do NOT proceed automatically on FAIL.

### Step 3: Generate Functional Specification (AI-Enhanced)
Using the parsed questionnaire data, generate the full functional specification (.docx) as defined in the `/payroll-funcspec` command, with AI design rationale, executive summary, and risk assessment:
- 14 sections translating business requirements to SAP functional design
- Full wage type catalog with processing/evaluation classes
- Work schedule rules and state-specific OT design (CA daily OT, 7th day, etc.)
- Benefits integration design (plans, eligibility, match formulas, imputed income)
- Tax authority design with local taxes and mandatory EE contributions
- Schema/PCR requirements
- Symbolic account mapping with cost center derivation
- Interface specifications
- Data migration design
- Traceability back to questionnaire sections

### Step 4: Generate Configuration Workbook (AI-Enhanced)
Using the functional specification generated in Step 3, create the configuration workbook (.xlsx) as defined in the `/payroll-config-workbook` command, with AI conflict detection, smart test scenarios, and per-row AI commentary:
- 21-tab workbook (20 data tabs + AI Analysis tab) with SAP field-level automation columns
- Enterprise Structure, PSA Groupings, Feature Configuration, Payroll Areas, Payroll Calendar
- Work Schedule Rules, Wage Type Catalog, Processing & Eval Classes, Wage Type Permissibility
- Pay Scale Structure, Tax Authorities, Absence & Quota Config
- Schema & PCR (manual), Garnishment Config (manual), Symbolic Accounts & GL Posting
- Interfaces (manual), Benefits Config (manual), House Bank Config
- Validation & Test Scenarios (with AI-generated smart scenarios)
- Traceability Matrix, AI Analysis Tab (conflict detection, readiness assessment)

### Step 5: AI Executive Briefing
After all documents are generated, use the LLM to create a **1-page Executive Briefing** (.docx) that synthesizes findings across ALL deliverables:
1. **Project Overview**: 2-3 sentence summary
2. **Scope Summary**: Employees, states, payroll areas, wage types, benefits, interfaces
3. **QA Risk Impact**: Key risks and their mitigation status from QA analysis
4. **Key Design Decisions**: Top 5 design decisions with business impact
5. **Configuration Readiness**: AUTO vs MANUAL tabs, estimated ABAP effort
6. **Implementation Risks**: Top 3 risks with probability, impact, and mitigation
7. **Recommended Next Steps**: Prioritized action items
8. **Timeline Considerations**: Effort estimates for remaining manual configuration

Written for CFO/VP HR audience — business-focused, minimal SAP jargon.

### Step 6: AI Cross-Document Integrity Check
Call the AI to verify traceability and consistency across ALL generated documents:
- Every questionnaire response → corresponding funcspec design decision
- Every funcspec design decision → corresponding config workbook entry
- Every config workbook entry → correct SAP table/field mapping
- Every critical configuration → test scenario in Tab 19
- Flag any breaks in the traceability chain as a final validation

## Output

Five deliverables saved to workspace outputs:
1. `SAP_Payroll_QA_Report_[CompanyName].docx` (with AI semantic analysis + risk narrative)
2. `SAP_Payroll_FuncSpec_[CompanyName].docx` (with AI design rationale + complexity assessment)
3. `SAP_Payroll_ConfigWorkbook_[CompanyName].xlsx` (with AI Analysis tab + smart test scenarios)
4. `SAP_Payroll_ExecutiveBriefing_[CompanyName].docx` (AI-generated cross-document synthesis)
5. Summary of all documents with links

Present all files to the user with:
- QA findings summary (pass/fail + AI risk narrative)
- FuncSpec section count, key design decisions, AI complexity ratings
- Config workbook tab count, total records, AI conflict report
- Executive briefing highlights
- Cross-document traceability confirmation
