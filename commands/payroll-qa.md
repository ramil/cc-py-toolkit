---
description: QA validate a completed payroll questionnaire
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, TodoWrite
argument-hint: <questionnaire.docx>
---

Quality-assure a completed SAP HCM Payroll Discovery Questionnaire. Read the uploaded questionnaire document, validate it for completeness and consistency, and produce a QA findings report.

Read the skill file at `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/SKILL.md` first. Then read ALL reference files from `${CLAUDE_PLUGIN_ROOT}/skills/sap-payroll-impl/references/` to have the full domain knowledge for validation.

## Input

The user will provide a completed questionnaire .docx file (either via upload or file path). Read and parse the entire document to extract all responses.

If no file is provided, ask the user to upload or specify the path to their completed questionnaire.

## QA Validation Checks

Perform these validation checks on the completed questionnaire, organized by category:

### 1. Completeness Check
- Identify any blank, empty, or placeholder responses (e.g., still contains "[Enter...]", "TBD", "N/A" without explanation)
- Flag sections with insufficient detail for SAP configuration
- Check that all 15 sections have responses
- List every gap found with section number and question reference

### 2. Enterprise Structure Consistency
- Verify all listed states have corresponding personnel areas
- Check that personnel subareas are defined for each PA
- Validate EE group/subgroup combinations are complete
- Confirm payroll area assignments cover all EE subgroups
- Verify holiday calendar exists for each state

### 3. Wage Type Completeness
- Check that all standard earnings categories are addressed (regular, OT, shift diff, absences, supplemental)
- Verify deduction wage types match the benefits plans listed
- Confirm employer contribution WTs exist for each benefit plan
- Flag any wage types mentioned but not fully defined
- Check for missing statutory deductions per state

### 4. Tax Configuration Validation
- Verify every state listed in Section 1 has tax details in Section 5
- Check that states with income tax have withholding method specified
- Validate SUI/SDI requirements per state
- Confirm W-4 version and supplemental tax method are specified
- Check for local tax requirements (NYC for NY, city taxes for OH/PA, etc.)
- Flag multi-state workers if mentioned but no allocation method specified

### 5. Benefits-Payroll Alignment
- Verify each benefit plan has corresponding EE deduction AND ER contribution wage types in Section 4
- Check 401(k) match formula is fully specified (tiers, caps, vesting)
- Validate FSA annual limits are within IRS limits
- Check group-term life for imputed income consideration (>$50K)
- Verify pre-tax vs. post-tax classification for each deduction

### 6. Time-Payroll Integration
- Verify time recording method is specified for each EE subgroup
- Check that OT calculation method aligns with state requirements (e.g., CA daily OT)
- Validate absence types have valuation rules and quota definitions
- Confirm shift definitions match shift differential wage types
- Check time source system interface is defined in Section 10

### 7. Garnishment Validation
- Verify CCPA priority ordering is correctly specified
- Check disposable income calculation includes all required deductions
- Validate state-specific garnishment rules for each operating state
- Confirm remittance methods are defined

### 8. Interface Completeness
- Verify all required outbound interfaces exist (FI posting, bank transfer, tax filing, 401k, benefits carriers)
- Check all required inbound interfaces exist (time data, at minimum)
- Validate each interface has: direction, format, frequency, protocol
- Flag any mentioned external systems without a corresponding interface

### 9. Cross-Section Consistency
- States in Section 1 match tax authorities in Section 5
- Benefits in Section 7 match deduction WTs in Section 4
- Time methods in Section 6 match interfaces in Section 10
- Pay frequencies in Section 3 match EE subgroup assignments in Section 2
- Migration source in Section 14 aligns with current system in Section 1

### 10. Go-Live Readiness
- Check that parallel run duration and approach are specified
- Verify go/no-go criteria are defined
- Confirm cutover sequence is documented
- Check that sign-off roles are appropriate for the organization

## AI-Powered Analysis

After performing all 10 rule-based validation checks above, use the LLM to perform deeper semantic analysis:

### AI Semantic Analyzer
For each free-text response in the questionnaire, call the AI to evaluate:
- **Completeness Score (1-5)**: Does this response provide enough detail for SAP table-level configuration?
- **Clarity Score (1-5)**: Is the response unambiguous? Could a different consultant interpret it differently?
- **SAP Readiness Score (1-5)**: Can this response be directly translated to SAP field values without further clarification?

Flag any response scoring below 3 on any dimension as an AI finding with specific recommendations.

### AI Contradiction Detector
Pass all cross-section responses to the AI as a bundle and ask it to identify:
- Logical contradictions (e.g., says "no union" in Section 1 but lists union dues WT in Section 4)
- Implicit gaps (e.g., mentions CA employees but no CA-specific sick leave or daily OT in Section 6)
- Scope creep indicators (e.g., mentions things in later sections that weren't set up in enterprise structure)

### AI Risk Narrative Generator
Based on all findings (both rule-based and AI-detected), call the AI to generate:
- A **2-3 paragraph executive risk narrative** suitable for a project steering committee
- Top 3 risks ranked by go-live impact
- Estimated remediation effort (hours/days) for each critical finding
- Specific mitigation recommendations

### AI Gap Predictor
Based on what WAS answered, call the AI to predict what's likely MISSING:
- "You mentioned 3-shift operations but did not specify shift differential amounts — this will be needed for wage type configuration"
- "You listed OH as an operating state but did not mention Columbus city tax — most OH manufacturers have employees in municipal tax jurisdictions"
- "401(k) match is mentioned but no catch-up or super catch-up provisions for employees 50+ / 60-63"

Insert AI findings into the report with a distinct marker: "🤖 AI Analysis" so they can be distinguished from rule-based findings.

## Output

Generate a QA Findings Report as a .docx file with:

### Summary Dashboard
- Overall completeness score (% of questions answered)
- Findings by severity: Critical (blocks config) / Warning (may cause issues) / Info (recommendation)
- Section-by-section readiness status (Ready / Needs Work / Incomplete)

### Detailed Findings
For each finding:
- **ID**: QA-001, QA-002, etc.
- **Section**: Which questionnaire section
- **Severity**: Critical / Warning / Info
- **Finding**: What was found
- **Impact**: Why this matters for SAP configuration
- **Recommendation**: What to do about it

### Cross-Reference Matrix
Table showing which questionnaire responses feed into which functional spec sections and config workbook tabs — highlighting any breaks in the traceability chain.

### Verdict
- PASS: Questionnaire is complete and consistent — ready to generate functional spec
- PASS WITH CONDITIONS: Minor gaps that can be resolved during functional spec creation
- FAIL: Critical gaps that must be addressed before proceeding

Format: Professional .docx, same styling as other deliverables (navy headers, Arial, tables).

Save to workspace outputs as `SAP_Payroll_QA_Report_[CompanyName].docx`.

## Output Self-Validation (LLM QA Gate)

**After generating the QA report .docx, perform an LLM-powered self-validation before presenting it to the user.** This ensures the QA report itself is complete, accurate, and actionable.

### Step 1: QA Report Structural Check
Read the generated QA report back and verify:
- Summary Dashboard is present with completeness score, finding counts, section-by-section status
- All 10 validation check categories have results (Completeness, Enterprise Structure, Wage Types, Tax, Benefits, Time, Garnishments, Interfaces, Cross-Section, Go-Live)
- Detailed Findings are numbered (QA-001, QA-002, etc.) with Section, Severity, Finding, Impact, Recommendation
- Cross-Reference Matrix is present
- Final Verdict (PASS / PASS WITH CONDITIONS / FAIL) is stated
- AI Analysis sections are present (Semantic Analyzer, Contradiction Detector, Risk Narrative, Gap Predictor)

### Step 2: LLM Consistency Review
Pass the full QA report content to the AI and ask it to verify:
1. **Finding accuracy**: Do the severity ratings (Critical/Warning/Info) match the actual impact described? Are any Critical findings under-rated?
2. **Recommendation actionability**: Can the client actually act on each recommendation? Are any recommendations too vague?
3. **Completeness of coverage**: Did the QA analysis miss any obvious issues visible in the questionnaire data?
4. **Verdict alignment**: Does the final verdict logically follow from the findings? (e.g., if there are 5+ Critical findings, verdict should be FAIL, not PASS WITH CONDITIONS)
5. **Cross-reference integrity**: Does the Cross-Reference Matrix correctly map questionnaire sections to functional spec and config workbook sections?

### Step 3: Auto-Fix and Report
- If the verdict doesn't match the findings, CORRECT IT
- If any validation category was skipped, ADD findings for it
- Append a **"📋 QA Report Validation"** note at the end:
  - Validation categories checked: X/10
  - Total findings: N (Critical: X, Warning: Y, Info: Z)
  - AI analysis sections: X/4
  - Self-validation: PASS / issues corrected

**Report the validation summary to the user when presenting the output.**

After presenting, ask the user if they want to:
1. Proceed to functional spec generation (if PASS or PASS WITH CONDITIONS)
2. Review and fix the questionnaire first (if FAIL)
