"""
AI Helper Module for SAP Payroll Implementation Toolkit
========================================================
Provides LLM-powered analysis functions that can be called from any command's
Python generation scripts. Uses the Anthropic API (Claude) for:
- Semantic analysis of questionnaire responses
- Risk narrative generation
- Design rationale writing
- Test scenario intelligence
- Employee scenario planning
- Configuration conflict detection

Usage:
    from ai_helper import PayrollAI
    ai = PayrollAI()  # Uses ANTHROPIC_API_KEY env var

    # Or pass key directly
    ai = PayrollAI(api_key="sk-ant-...")

    result = ai.analyze_questionnaire_response(section, question, response)
    narrative = ai.generate_risk_narrative(findings)
    rationale = ai.generate_design_rationale(section, design_decisions)
"""

import os
import json
from typing import Optional

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class PayrollAI:
    """LLM-powered analysis engine for SAP Payroll implementation documents."""

    MODEL = "claude-sonnet-4-5-20250929"
    MAX_TOKENS = 2048

    SYSTEM_PROMPT = """You are an expert SAP HCM US Payroll implementation consultant
with 15+ years of experience configuring SAP ECC payroll (Molga 10) for mid-market
and enterprise companies. You have deep knowledge of:
- Enterprise structure design (T001P, T503, T589E)
- Wage type architecture (V_T511, V_T52D0, V_T52D1)
- BSI TaxFactory tax configuration (V_T5UTZ, V_T5UTY)
- Work schedule rules and state-specific OT (CA daily OT, 7th day)
- Benefits integration (401k match, imputed income)
- Garnishment processing (CCPA priority, state variations)
- Payroll schemas and PCRs (U000, custom PCRs)
- FI posting and symbolic accounts (V_T52EL, V_T52E4)
- LSMW data migration

You provide concise, actionable analysis in professional consulting language.
Avoid generic advice — be specific to SAP payroll configuration."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if HAS_ANTHROPIC and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False

    def _call_llm(self, prompt: str, max_tokens: int = None) -> str:
        """Call the Anthropic API. Returns empty string if unavailable."""
        if not self.enabled:
            return ""
        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=max_tokens or self.MAX_TOKENS,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"[AI analysis unavailable: {e}]"

    # =========================================================================
    # QUESTIONNAIRE AI FEATURES
    # =========================================================================

    def generate_industry_profile(self, company_name: str, industry: str,
                                   headcount: int, states: list) -> str:
        """Generate industry-specific questionnaire guidance."""
        prompt = f"""For a company named "{company_name}" in the {industry} industry
with {headcount} employees across {', '.join(states)}, generate a brief
industry-specific guidance note (3-5 paragraphs) covering:

1. Common payroll complexities for this industry (e.g., tip wages for hospitality,
   prevailing wage for construction, shift differentials for manufacturing)
2. State-specific considerations for their operating states
3. Typical benefit plan structures for this industry/size
4. Common integration points and data migration challenges
5. Key risk areas to probe during discovery

Keep it under 500 words. Use bullet points sparingly."""
        return self._call_llm(prompt)

    def suggest_industry_questions(self, industry: str) -> str:
        """Suggest additional industry-specific questions for the questionnaire."""
        prompt = f"""For the {industry} industry, suggest 5-8 additional SAP payroll
discovery questions that are NOT in the standard 15-section questionnaire.
Format as a numbered list with the question and WHY it matters for SAP config.

Examples of industry-specific concerns:
- Healthcare: on-call/callback pay, PRN/per diem, credential premiums
- Manufacturing: prevailing wage, shift rotation, hazard pay, piece rate
- Retail: tip credit, split shift premium, seasonal hiring
- Construction: Davis-Bacon, certified payroll, multi-state job costing
- Technology: RSU/stock options, global mobility, remote work tax nexus

Only include questions relevant to {industry}."""
        return self._call_llm(prompt)

    # =========================================================================
    # QA AI FEATURES
    # =========================================================================

    def analyze_response_quality(self, section: str, question: str,
                                  response: str) -> dict:
        """Analyze a questionnaire response for completeness and clarity."""
        prompt = f"""Analyze this SAP payroll questionnaire response:

Section: {section}
Question: {question}
Response: {response}

Evaluate on a 1-5 scale:
1. Completeness: Does it provide enough detail for SAP configuration?
2. Clarity: Is it unambiguous? Could it be misinterpreted?
3. SAP Readiness: Can this be directly translated to SAP table values?

Return JSON format:
{{
  "completeness_score": <1-5>,
  "clarity_score": <1-5>,
  "sap_readiness_score": <1-5>,
  "issues": ["list of specific issues found"],
  "missing_details": ["what additional info is needed"],
  "recommendation": "one sentence recommendation"
}}"""
        result = self._call_llm(prompt)
        try:
            return json.loads(result)
        except:
            return {"completeness_score": 0, "raw_analysis": result}

    def detect_contradictions(self, responses: dict) -> str:
        """Detect contradictions across questionnaire sections."""
        prompt = f"""Review these SAP payroll questionnaire responses across sections
and identify any contradictions, inconsistencies, or logical conflicts:

{json.dumps(responses, indent=2)}

For each contradiction found, explain:
1. Which sections conflict
2. What the contradiction is
3. Why it matters for SAP configuration
4. How to resolve it

If no contradictions found, say "No contradictions detected." """
        return self._call_llm(prompt, max_tokens=3000)

    def generate_risk_narrative(self, findings: list) -> str:
        """Generate a risk assessment narrative from QA findings."""
        prompt = f"""Based on these QA findings from an SAP payroll questionnaire review,
write a 2-3 paragraph executive risk assessment narrative:

Findings:
{json.dumps(findings, indent=2)}

The narrative should:
1. Summarize the overall risk level (Low/Medium/High)
2. Highlight the top 3 risks that could impact go-live
3. Recommend specific mitigation actions
4. Estimate the effort to resolve (hours/days)

Write in professional consulting language suitable for a project steering committee."""
        return self._call_llm(prompt)

    def predict_missing_config(self, answered_sections: dict) -> str:
        """Predict what configuration areas might be missing based on what was answered."""
        prompt = f"""Based on what was answered in this SAP payroll questionnaire,
predict what configuration areas are likely MISSING or under-specified:

Answered sections summary:
{json.dumps(answered_sections, indent=2)}

Consider:
- If they mention CA employees but no CA daily OT rules → likely gap
- If they mention union but no H&W fund or pension → likely gap
- If they mention multi-state but no reciprocity → likely gap
- If they mention 401k but no match formula tiers → likely gap
- If they mention shifts but no shift differential amounts → likely gap

List each predicted gap with severity (Critical/Warning/Info) and what
questions to ask the client to fill the gap."""
        return self._call_llm(prompt, max_tokens=3000)

    # =========================================================================
    # FUNCSPEC AI FEATURES
    # =========================================================================

    def generate_design_rationale(self, section: str, decisions: dict) -> str:
        """Generate design rationale explaining WHY decisions were made."""
        prompt = f"""For this SAP payroll functional spec section, write a
design rationale paragraph (150-250 words) explaining WHY these design
decisions were made — not just WHAT they are:

Section: {section}
Design Decisions:
{json.dumps(decisions, indent=2)}

The rationale should:
1. Explain the business driver behind each decision
2. Note any SAP best practices being followed
3. Flag any trade-offs or alternatives that were considered
4. Reference relevant SAP tables/transactions

Write in first-person plural ("We recommend..." / "The design leverages...")."""
        return self._call_llm(prompt)

    def assess_complexity_risk(self, config_summary: dict) -> str:
        """Assess implementation complexity and risk for each funcspec area."""
        prompt = f"""Assess the implementation complexity and risk for this
SAP payroll configuration:

{json.dumps(config_summary, indent=2)}

For each area, provide:
1. Complexity rating: Simple / Moderate / Complex / Very Complex
2. Risk level: Low / Medium / High
3. Estimated configuration effort (hours)
4. Key risk factors
5. Recommended testing approach

Format as a table with columns: Area | Complexity | Risk | Effort (hrs) | Key Risks | Test Approach"""
        return self._call_llm(prompt, max_tokens=3000)

    def generate_executive_summary(self, company_name: str,
                                    scope_summary: dict) -> str:
        """Generate an executive summary for the functional specification."""
        prompt = f"""Write a 300-400 word executive summary for the SAP HCM
Payroll Functional Specification for {company_name}:

Scope:
{json.dumps(scope_summary, indent=2)}

The summary should:
1. State the project objective (SAP ECC US Payroll implementation)
2. Summarize the scope (# employees, # states, # payroll areas, key features)
3. Highlight key design decisions and their business impact
4. Note any complex areas requiring special attention
5. State dependencies and assumptions
6. Provide a high-level timeline reference

Write in executive briefing style — concise, authoritative, no jargon."""
        return self._call_llm(prompt)

    # =========================================================================
    # CONFIG WORKBOOK AI FEATURES
    # =========================================================================

    def generate_config_commentary(self, tab_name: str, config_data: dict) -> str:
        """Generate AI commentary for a config workbook tab."""
        prompt = f"""Write a concise analysis paragraph (100-150 words) for
this SAP payroll configuration tab:

Tab: {tab_name}
Configuration Data:
{json.dumps(config_data, indent=2)}

The commentary should:
1. Summarize what was configured and why
2. Flag any potential conflicts or issues
3. Note dependencies on other tabs
4. Recommend validation steps

Write in technical consulting language."""
        return self._call_llm(prompt)

    def detect_config_conflicts(self, all_tabs_summary: dict) -> str:
        """Detect potential conflicts across config workbook tabs."""
        prompt = f"""Review this SAP payroll configuration workbook summary
and identify potential cross-tab conflicts:

{json.dumps(all_tabs_summary, indent=2)}

Common conflict patterns to check:
- Wage types assigned to subgroups that don't exist in enterprise structure
- Tax authorities without matching payroll areas
- Benefits WTs not in wage type catalog
- WSR codes referenced but not defined
- Symbolic accounts referencing undefined wage types
- Pay scale groupings not matching PSA assignments
- Absence quota types without matching wage types

For each conflict, explain what it is, which tabs are involved,
and how to fix it."""
        return self._call_llm(prompt, max_tokens=3000)

    def generate_smart_test_scenarios(self, config_summary: dict,
                                       states: list) -> str:
        """Generate intelligent test scenarios based on actual configuration."""
        prompt = f"""Based on this SAP payroll configuration, generate 15-20
detailed test scenarios that cover the most critical and edge-case situations:

Configuration:
{json.dumps(config_summary, indent=2)}
Operating States: {', '.join(states)}

For each test scenario, provide:
- Test ID (TC-001 format)
- Category (Regular Pay / OT / Tax / Deduction / Benefit / Garnishment / Absence / Posting / Off-Cycle)
- Description (specific scenario, not generic)
- Employee type and state
- Input values (hours, rates, deductions)
- Expected gross, deductions, taxes, net (approximate)
- What SAP transaction to verify (PC00_M10_CALC_SIMU, PT60, RPCIPTU0)
- Why this test matters

Prioritize scenarios that:
1. Test state-specific rules (CA daily OT, TX no state tax)
2. Test edge cases (max 401k, SS wage base exceeded, multi-state)
3. Test complex interactions (OT + shift diff + garnishment)
4. Test year-end (W-2 box mapping, GTL imputed income)

Format as JSON array."""
        return self._call_llm(prompt, max_tokens=4000)

    # =========================================================================
    # MIGRATION FILE AI FEATURES
    # =========================================================================

    def plan_employee_scenarios(self, config_summary: dict) -> str:
        """Plan employee scenarios that thoroughly test all configuration."""
        prompt = f"""Based on this SAP payroll configuration, plan 12-18
employee scenarios that collectively cover ALL configured elements:

Configuration:
{json.dumps(config_summary, indent=2)}

For each employee scenario, specify:
- Employee # and name pattern
- EE Group/Subgroup
- Personnel Area/Subarea
- State (residence + work if different)
- Payroll Area
- Work Schedule Rule
- Pay type (salary/hourly) and rate
- Deductions (which ones, amounts)
- Benefits enrollments
- Special attributes (union, garnishment, mid-year hire, multi-state)

Design the scenarios so that:
1. Every PA/PSA is used at least once
2. Every payroll area is used at least once
3. Every EE Subgroup is used at least once
4. Every state has at least one employee
5. Multi-state scenario exists (live in one state, work in another)
6. CA employee tests daily OT
7. Union employee tests dues + H&W + pension
8. At least one garnishment scenario
9. At least one mid-year hire (for YTD testing)
10. Executive for high-comp scenarios (SS wage base, additional Medicare)

Format as JSON array."""
        return self._call_llm(prompt, max_tokens=4000)

    def review_migration_data(self, data_summary: dict) -> str:
        """Review generated migration data for completeness and realism."""
        prompt = f"""Review this SAP payroll migration data summary and
identify any issues:

{json.dumps(data_summary, indent=2)}

Check for:
1. Unrealistic salary amounts (too low for executives, too high for hourly)
2. Missing infotype records (everyone needs IT0000, IT0001, IT0002, IT0006, IT0007, IT0008)
3. Tax area mismatches (IT0207 residence should match IT0006 address state)
4. Benefit enrollment vs eligibility (part-time shouldn't have FT-only benefits)
5. Work schedule rule vs EE subgroup mismatch
6. Deduction amounts vs annual limits (401k over $23,500)
7. Missing multi-row records (IT0014 should have multiple rows per employee)
8. Union employees without union-specific deductions
9. Garnishment employees without IT0194 records

For each issue, state what it is, which employee is affected, and how to fix it."""
        return self._call_llm(prompt, max_tokens=3000)

    # =========================================================================
    # PIPELINE AI FEATURES
    # =========================================================================

    def generate_executive_briefing(self, project_data: dict) -> str:
        """Generate a cross-document executive briefing for the full pipeline."""
        prompt = f"""Write a 1-page executive briefing for this SAP HCM Payroll
implementation project based on all generated documents:

{json.dumps(project_data, indent=2)}

Structure:
1. **Project Overview** (2-3 sentences)
2. **Scope Summary** (bullet points: employees, states, payroll areas,
   wage types, benefits plans, interfaces)
3. **Key Design Decisions** (top 5 decisions and their business impact)
4. **Risk Assessment** (top 3 risks with mitigation)
5. **Configuration Readiness** (% of tabs automation-ready, manual items)
6. **Recommended Next Steps** (prioritized action items)
7. **Timeline Impact** (estimated effort for remaining manual items)

Write for a CFO/VP HR audience — business-focused, minimal SAP jargon."""
        return self._call_llm(prompt, max_tokens=3000)


# =========================================================================
# STANDALONE FUNCTIONS (no API key needed — use Claude's own reasoning)
# =========================================================================

def build_ai_analysis_prompt(context: str, task: str) -> str:
    """Build a structured prompt for Claude to perform AI analysis
    during command execution (no API call needed — Claude IS the LLM)."""
    return f"""## AI Analysis Task

**Context:**
{context}

**Task:**
{task}

**Instructions:**
- Be specific to SAP HCM US Payroll (Molga 10)
- Reference actual SAP tables, views, and transactions
- Provide actionable recommendations
- Use professional consulting language
- Keep response concise (under 300 words unless otherwise specified)
"""
