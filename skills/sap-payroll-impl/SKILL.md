---
name: sap-payroll-impl
description: >
  This skill should be used when the user asks to "implement SAP payroll",
  "set up SAP HCM payroll", "configure US payroll in SAP", "create a payroll questionnaire",
  "build a payroll functional spec", "generate payroll configuration", "SAP payroll implementation",
  "payroll go-live", "payroll cutover", "QA the questionnaire", "validate questionnaire",
  "generate migration file", "hiring data migration", "LSMW template", "employee data load",
  or needs guidance on SAP ECC/S4HANA US payroll enterprise structure, wage types,
  tax authorities, schemas, PCRs, BSI TaxFactory, garnishments, FI posting, or payroll interfaces.
version: 1.0.0
---

# SAP HCM US Payroll Implementation Skill (AI-Enhanced)

Guide users through SAP HCM US Payroll (Molga 10) implementations using an AI-enhanced, document-driven pipeline where the completed questionnaire is the single source of truth for all downstream deliverables. Every command leverages LLM intelligence for semantic analysis, design rationale, conflict detection, and executive-level synthesis.

## Core Deliverables

1. **Payroll Discovery Questionnaire** (.docx) — AI-enhanced blank template with 15 sections + Section 1A Implementation Approach Decisions + industry-specific guidance. Section 1A captures 5 critical architectural toggles (Time Management Approach, Benefits Approach, OM Scope, Go-Live Timing, Concurrent Employment) that cascade through all downstream deliverables. The LLM analyzes the company's industry to generate customized guidance inserts, industry-specific questions, and state compliance alerts. Covers: company overview, approach decisions, enterprise structure, payroll areas, wage types, tax config, time management, benefits, garnishments, off-cycle, interfaces, reporting, year-end, security, data migration, and sign-off.

2. **QA Validation Report** (.docx) — AI-powered validation with 10 rule-based checks PLUS LLM semantic analysis (completeness/clarity/SAP-readiness scoring per response), contradiction detection across sections, predictive gap analysis ("you mentioned X but didn't address Y"), and executive risk narrative generation. Provides PASS/FAIL verdict with AI-generated mitigation recommendations.

3. **Functional Specification** (.docx) — AI-enriched SAP functional design with LLM-generated executive summary, per-section design rationale explaining WHY decisions were made, complexity & risk assessment table, and cross-reference integrity check. Covers: wage type catalog, work schedule rules, benefits integration, tax authority design, schema/PCR requirements, symbolic account mapping, interface specs, and migration design.

4. **Configuration Workbook** (.xlsx) — 21-tab automation-ready workbook (20 data tabs + AI Analysis tab). Automatable tabs include SAP field-level columns for ABAP report consumption. The AI Analysis tab contains: configuration summary narrative, cross-tab conflict detection report, automation readiness assessment, and AI-generated smart test scenarios tailored to the actual configuration. Per-row AI commentary flags non-standard configurations and best practice recommendations.

5. **Hiring Data Migration File** (.xlsx) — 18-22 sheet Excel file with AI-planned employee scenarios, adapting to the chosen approach (Full Benefits vs Deductions-Only, Full Time vs Negative Time, etc.). Includes new infotypes: IT0003 (Payroll Status), IT0041 (Date Specifications), IT0105 (Communication), and IT0027 (Cost Distribution, if concurrent employment). The LLM designs employee profiles that collectively cover ALL configured elements. Includes AI data quality review sheet checking salary reasonableness, tax area alignment, benefits eligibility, and deduction limits.

6. **Executive Briefing** (.docx) — AI-generated cross-document synthesis for CFO/VP HR audience. Covers project scope, key design decisions, QA risk impact, configuration readiness, implementation risks, and recommended next steps. Only generated via the `/payroll-implement` full pipeline command.

## AI Integration Architecture

The toolkit uses LLM calls at strategic points in the pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│  AI LAYER (LLM Calls)                                        │
│                                                               │
│  Questionnaire:  Industry Profiler → State Alerts             │
│  QA:             Semantic Analyzer → Contradiction Detector   │
│                  → Risk Narrator → Gap Predictor              │
│  FuncSpec:       Executive Summary → Design Rationale         │
│                  → Complexity Assessment → Integrity Check    │
│  Config WB:      Conflict Detector → Smart Test Generator     │
│                  → Readiness Assessment → Per-Row Commentary  │
│  Migration:      Scenario Planner → Data Quality Reviewer     │
│  Pipeline:       Executive Briefing → Cross-Doc Integrity     │
└─────────────────────────────────────────────────────────────┘
```

The AI helper module (`lib/ai_helper.py`) provides a `PayrollAI` class that can optionally call the Anthropic API for batch processing. When running inside Claude (Cowork/Claude Code), the LLM analysis is performed natively by Claude during command execution.

## Document-Driven Pipeline

The questionnaire is the **single source of truth**. All downstream documents are generated from it:

```
/payroll-questionnaire → AI-profiled blank template for consultant discovery
         ↓ (consultant fills during client sessions)
/payroll-qa [questionnaire.docx] → AI-powered validation + risk narrative
         ↓ (PASS or PASS WITH CONDITIONS)
/payroll-funcspec [questionnaire.docx] → AI-enriched SAP functional design + rationale
         ↓ (generates funcspec.docx)
/payroll-config-workbook [funcspec.docx] → Automation-ready config + AI analysis tab
         ↓ (generates config workbook)
/payroll-migration-file [config-workbook.xlsx] → AI-planned migration data + quality review
```

Or run the full AI-enhanced pipeline in one shot:
```
/payroll-implement [questionnaire.docx] → QA → FuncSpec → Config → Executive Briefing
```

Then generate migration data:
```
/payroll-migration-file [config-workbook.xlsx] → AI-planned employee scenarios + data review
```

Each config item traces back to a functional spec section, which traces back to a questionnaire response, which traces to a test scenario.

## Reference Files

Domain knowledge for translating business requirements into SAP configuration is in `references/`:

- `references/enterprise-structure.md` — PA, PSA, EE Group/Subgroup, features (ABKRS, SCHKZ), union config
- `references/wage-types.md` — Full WT catalog, processing/eval classes, industry WTs (healthcare, manufacturing, retail), permissibility matrix, cumulation config
- `references/tax-configuration.md` — BSI TaxFactory, all 50 states, flat vs progressive, local taxes, mandatory EE contributions (SDI/PFL/PFML/WA Cares), IT0210 by state, deposit schedules, year-end
- `references/schemas-pcrs.md` — Schema U000 structure, common custom PCRs (CA daily OT, 401k match, imputed income, shift diff, PTO accrual, supplemental tax)
- `references/garnishments.md` — CCPA priority, disposable income (detailed calculation), state variations (CA, NY, IL, FL, TX, PA, MA, NJ, OH, OR, WA), garnishment fees
- `references/interfaces.md` — Standard SAP payroll interfaces and file formats
- `references/fi-posting.md` — Symbolic accounts, GL mapping, posting variants (V_T52EK), cost distribution (IT0027), period-end close
- `references/data-migration.md` — ADP/legacy migration, IT0559/0560, parallel run
- `references/work-schedules-ot.md` — WSR definitions (T508A, T550A, T551A), state-specific OT rules (CA daily/7th day, CO, AK, NV), shift differentials, weighted average OT, meal/rest breaks by state, holiday pay
- `references/benefits-config.md` — Benefit plan types (IT0167-0171), 401k match formulas (simple/tiered/safe harbor), HSA/FSA/DCFSA, union H&W/pension, eligibility rules, vesting, IRS annual limits, ACA tracking, imputed income (IRS Table I)

## Document Generation

**For .docx files** (Questionnaire, QA Report, Functional Spec):
- Use the `docx` npm package (docx-js)
- US Letter page size (12240 x 15840 DXA)
- Professional formatting: Arial font, navy headers (#1F4E79), table borders
- Include Table of Contents, headers/footers with page numbers
- Validate with the docx validation script

**For .xlsx files** (Configuration Workbook):
- Use openpyxl Python library
- 16 tabs with Cover/Index listing all tabs and record counts
- Professional styling: navy header row (#1F4E79, white text), auto-filters, freeze panes at row 4
- Light yellow fill on cells requiring client input
- Data validation dropdowns (Y/N, pre/post tax, etc.)
- Conditional formatting: red fill on "MISSING" or "TBD" cells
- Column widths optimized for content readability
- Recalculate with the recalc script if formulas are used

## SAP Payroll Key Concepts

### Enterprise Structure Hierarchy
```
Company Code (T001)
  └── Personnel Area (T001P) — physical location
        └── Personnel Subarea — functional grouping (PSA groupings control pay scale, wage types, absences)
              └── Employee Group (T501) — active/retiree/external
                    └── Employee Subgroup (T503K) — exempt/non-exempt/executive/union
```

### Feature Defaulting (PE03)
- ABKRS: Payroll area from EE Group/Subgroup/PA/PSA
- SCHKZ: Work schedule rule from PSA + EE Subgroup
- LGMST: Legal entity from personnel area
- TARIF: Pay scale type/area

### Payroll Processing Flow
```
1. Lock payroll period (PU03)
2. Time evaluation (RPTIME00 / PT60)
3. Payroll simulation (PC00_M10_CALC_SIMU)
4. Review & correct (PCC alerts)
5. Release for live run
6. Live payroll (PC00_M10_CALC)
7. Bank transfer (RFFOUS_T)
8. FI posting (RPCIPTU0)
9. Reporting & reconciliation (RPCPRRU0)
```

### Wage Type Ranges (US Payroll)
- **1000-1999**: Custom earnings (copied from model M-series)
- **2000-2999**: Custom deductions (copied from model D-series)
- **3000-3999**: Custom employer contributions (copied from model E-series)
- **/100-/999**: SAP technical wage types (system-generated)

### Key Processing Classes
| PC | Controls | Critical Values |
|----|----------|----------------|
| 01 | EE grouping permissibility | Which EE subgroups can receive the WT |
| 02 | Time processing | 1=time-based, 2=lump sum, 3=OT, 5=absence |
| 03 | Cumulation | Maps to /3xx cumulation WTs |
| 10 | Tax treatment | 01=regular, 02=supplemental, 03=non-taxable |
| 20 | Garnishment inclusion | 01=include in disposable, 02=exclude |
| 30 | Benefits base | 01=include, 02=exclude |
| 40 | 401(k) eligible comp | 01=include, 02=exclude |
| 71 | FI posting indicator | Symbolic account assignment |

### Tax Framework (BSI TaxFactory)
- BSI handles all federal/state/local tax calculations
- IT0207 (Residence) + IT0208 (Work Tax Area) provide geocodes
- IT0210 holds W-4 data and state withholding elections (subtype per state)
- 9 states with no income tax: AK, FL, NV, NH, SD, TN, TX, WA, WY
- Mandatory EE contributions: CA SDI, NJ TDI/FLI, NY DBL/PFL, HI TDI, WA PFML, MA PFML, CO FAMLI, etc.
- Quarterly updates via SAP Support Packages + BSI patches
- ADP SmartCompliance or similar for tax filing (941, W-2)

### Overtime Rules (Key States)
- **Federal (FLSA)**: Weekly >40h = 1.5x (non-exempt only)
- **California**: Daily >8h = 1.5x, >12h = 2.0x, 7th consecutive day = 2.0x
- **Colorado**: Daily >12h = 1.5x
- **Alaska/Nevada**: Daily >8h = 1.5x

Read reference files as needed for detailed configuration values and patterns.
