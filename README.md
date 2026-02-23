# cc-py-toolkit v2.0.0

AI-Enhanced SAP HCM Payroll Implementation Toolkit for Claude Cowork. A document-driven pipeline with LLM-powered analysis for SAP ECC/S4HANA US Payroll (Molga 10) implementations where the completed questionnaire is the single source of truth.

**v2.0.0**: Battle-tested to 100% validation across 50 companies, 20 industries, 7 approach combinations. Includes deterministic generation library and iterative testing framework.

## How It Works

The plugin follows a structured implementation workflow with AI analysis at every stage:

```
Step 1: /payroll-questionnaire          → Generate blank template (+ AI industry profiling)
Step 2: Consultant fills it out         → During client discovery sessions
Step 3: /payroll-qa questionnaire.docx  → Validate completeness (+ AI semantic analysis)
Step 4: /payroll-funcspec questionnaire.docx   → Generate functional spec (+ AI design rationale)
Step 5: /payroll-config-workbook funcspec.docx → Generate config workbook (+ AI conflict detection)
Step 6: /payroll-migration-file config.xlsx    → Generate migration file (+ AI scenario planning)
```

Or run steps 3-6 in one shot: `/payroll-implement questionnaire.docx`

## Deliverables

1. **Payroll Discovery Questionnaire** (.docx) — Blank 15-section template with AI-generated industry profiling, state-specific compliance alerts, and industry-tailored supplemental questions.

2. **QA Validation Report** (.docx) — Validates completeness, cross-section consistency, and SAP readiness with AI semantic scoring, contradiction detection, risk narrative, and gap prediction.

3. **Functional Specification** (.docx) — Translates questionnaire answers into SAP functional design with AI-generated executive summary, design rationale callouts, and complexity assessment.

4. **Configuration Workbook** (.xlsx) — 21-tab Excel workbook with SAP field-level automation columns. All GL accounts (HKONT) populated, tax rates filled, SAP field names in headers. Approach-driven depth: tab existence is mandatory, only row count varies by approach.

5. **Hiring Data Migration File** (.xlsx) — 18-23 sheet Excel file with infotype-based employee records (IT0000-IT2006). Full BSI geocode mapping, multi-row compliance, conditional sheets for garnishments, mid-year YTD, concurrent employment, and approach-aware benefits.

6. **Executive Briefing** (.docx) — AI-generated 1-page cross-document synthesis. (Pipeline command only.)

## Commands

| Command | Input | Output |
|---------|-------|--------|
| `/payroll-questionnaire [company]` | Company name (optional) | Blank questionnaire template (.docx) |
| `/payroll-qa <questionnaire.docx>` | Completed questionnaire | QA validation report (.docx) |
| `/payroll-funcspec <questionnaire.docx>` | Completed questionnaire | Functional specification (.docx) |
| `/payroll-config-workbook <funcspec.docx>` | Functional specification | Config workbook (.xlsx) |
| `/payroll-migration-file <config.xlsx>` | Configuration workbook | Migration file (.xlsx) |
| `/payroll-implement <questionnaire.docx>` | Completed questionnaire | All deliverables + Executive Briefing |

## Skills

| Skill | Description |
|-------|-------------|
| `sap-payroll-impl` | SAP US Payroll implementation domain knowledge with 10 reference files, gen_helpers.py, and testing framework |

## Included Libraries

| File | Purpose |
|------|---------|
| `lib/gen_helpers.py` | Deterministic config workbook + migration file generation (1,183 lines) |
| `lib/ai_helper.py` | LLM-powered analysis functions (PayrollAI class) |
| `testing/validator.py` | v3 validator with 44+ automated checks |
| `testing/test_harness.py` | 50 company profiles across 20 industries |
| `testing/wave_runner.py` | Batch generation, validation, and error tracking orchestration |
| `testing/error_registry.json` | Cumulative error history across 11 waves (51 errors tracked) |

## Domain Coverage (10 Reference Files)

Enterprise structure, wage types, processing classes, BSI TaxFactory (all 50 states), work schedules (CA/CO/AK/NV OT), benefits (401k, HSA/FSA, union H&W), garnishments (CCPA priority), FI posting, schemas/PCRs, interfaces, and data migration.

## Requirements

- Claude Cowork with docx and xlsx skills available
- Python `openpyxl` package (for Excel workbook generation)
- npm `docx` package (for Word document generation)
- Python `anthropic` package (optional — for external AI API calls)
