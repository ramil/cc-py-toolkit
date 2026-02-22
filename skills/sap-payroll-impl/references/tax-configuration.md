# Tax Configuration Reference

## BSI TaxFactory Integration

### Architecture
- BSI TaxFactory is the tax calculation engine embedded in SAP US Payroll
- SAP calls BSI via function module HR_BSI_TAXFACTORY during schema U000
- BSI handles all federal, state, and local tax calculations
- Tax tables updated quarterly via SAP Support Packages + BSI patches

### Key SAP Notes
- 2310085: BSI TaxFactory configuration and troubleshooting
- 2552972: PCC integration with BSI
- Quarterly tax update notes (search "BSI" in SAP Support Portal)

## Tax Authority Setup (V_T5UTZ / V_T5UTY)

### Federal
| Field | Value |
|-------|-------|
| Authority | FED |
| BSI Code | 00 |
| Tax Types | FITW (income), FICA-SS, FICA-Med, FUTA |
| IT0210 Subtype | 01 |
| W-4 Version | 2020+ (Step 1-4 format) |

### State Tax Summary
| State | BSI Code | Income Tax | Rate | SUI Wage Base | SDI/PFL |
|-------|----------|-----------|------|---------------|---------|
| AL | 01 | Yes | 2-5% progressive | $8,000 | No |
| CA | 05 | Yes | 1-13.3% progressive | $7,000 | SDI: 1.1% |
| CO | 06 | Yes | 4.4% flat | $20,400 | FAMLI |
| CT | 07 | Yes | 3-6.99% progressive | $15,000 | CT PFL |
| FL | 10 | No | N/A | $7,000 | No |
| GA | 11 | Yes | 1-5.49% progressive | $9,500 | No |
| HI | 12 | Yes | 1.4-11% progressive | $56,700 | TDI |
| IL | 14 | Yes | 4.95% flat | $13,590 | No |
| MA | 22 | Yes | 5% flat + 4% surtax >$1M | $15,000 | PFML |
| NJ | 31 | Yes | 1.4-10.75% progressive | $41,400 | TDI, FLI |
| NY | 33 | Yes | 4-10.9% progressive | $12,500 | SDI, PFL |
| PA | 39 | Yes | 3.07% flat | $10,000 | No |
| TX | 43 | No | N/A | $9,000 | No |
| WA | 48 | No | N/A | $67,600 | PFML, WA Cares |

### Local Tax Authorities
| Local | Parent State | BSI Geocode | Tax Type |
|-------|-------------|-------------|----------|
| New York City | NY (33) | 33-051-0000 | Resident income tax |
| Yonkers | NY (33) | 33-121-0000 | Resident/non-resident |
| Philadelphia | PA (39) | 39-101-0000 | Wage tax |
| Various OH cities | OH (36) | 36-xxx-0000 | Municipal income tax |

## Tax Infotype Design

### IT0207 - Residence Tax Area
- Employee's home address for resident tax determination
- BSI resolves zip code to geocode (state + county + city)
- One active record per employee
- Used for: resident state tax, local tax (where applicable)

### IT0208 - Work Tax Area
- Employee's work location for work-state tax
- Can have multiple records for multi-state workers (allocation %)
- BSI resolves zip code to geocode
- Used for: work state tax, SUI jurisdiction

### IT0210 - Withholding Info
- One record per tax authority per employee
- Subtypes correspond to BSI state codes (01=Federal, 05=CA, etc.)

### IT0210 Fields (Federal - 2020+ W-4)
| Field | Description | W-4 Step |
|-------|-------------|----------|
| Filing Status | Single, MFJ, HoH | Step 1(c) |
| Multiple Jobs | Two earners/multiple jobs checkbox | Step 2(c) |
| Dependents Amount | Total claim amount for dependents | Step 3 |
| Other Income | Other income amount | Step 4(a) |
| Deductions | Deductions amount (above standard) | Step 4(b) |
| Extra Withholding | Additional withholding per pay period | Step 4(c) |

### IT0210 Fields (State)
Varies by state. Common fields:
- Filing status (state-specific statuses)
- Allowances / exemptions
- Additional withholding
- State-specific forms (DE 4 for CA, IT-2104 for NY, IL-W-4)

## Multi-State Tax Processing

### Resident vs. Work State
- Employee taxed by both resident state and work state
- Credit mechanism prevents double taxation (usually)
- SAP/BSI automatically handles credit calculations

### Reciprocity Agreements
- Some states agree not to tax non-resident workers
- Configured in BSI; suppresses work-state withholding
- Common pairs: IL-WI, IL-IA, IL-KY, IL-MI, VA-DC-MD, PA-NJ (limited)

### Multi-State Workers (Travel/Remote)
- IT0210 supports multiple work-state records with allocation %
- Days-worked allocation: % based on actual days in each state
- Some states have de minimis thresholds (e.g., "convenience of employer" rules)

## Supplemental Tax Method
- Federal: Flat 22% on supplemental wages (or aggregate if > $1M: 37%)
- State: Varies — some have flat supplemental rates, others use aggregate
- BSI handles method selection based on wage type processing class 10

## Additional Medicare Tax
- 0.9% additional on wages > $200K (single) / $250K (MFJ)
- BSI tracks YTD accumulator automatically
- No employer match on additional Medicare

## Tax Filing and Reporting
| Report | Frequency | Method |
|--------|-----------|--------|
| Federal 941 | Quarterly | ADP SmartCompliance or equivalent |
| Federal 940 (FUTA) | Annual | ADP SmartCompliance |
| State SUI | Quarterly | Per state filing |
| W-2 / W-3 | Annual (Jan 31) | RPCTWNU0 extract + filing service |
| W-2c | As needed | Correction via filing service |
| State W-2 copies | Annual | Per state requirements |
| 1095-C (ACA) | Annual (March) | SAP or third-party |

## States with No Income Tax (9)
Alaska, Florida, Nevada, New Hampshire (interest/dividends only until 2027), South Dakota, Tennessee, Texas, Washington, Wyoming

## States with Flat Income Tax
| State | Rate | Notes |
|-------|------|-------|
| CO | 4.40% | Flat |
| IL | 4.95% | Flat |
| IN | 3.05% | Plus county taxes |
| KY | 4.00% | Flat (effective 2024) |
| MI | 4.25% | Some cities add |
| NC | 4.50% | Trending down |
| PA | 3.07% | Flat; no standard deduction |
| UT | 4.65% | Flat |

## Mandatory EE Contributions by State
| State | Program | EE Rate | Wage Base |
|-------|---------|---------|-----------|
| CA | SDI/PFL | ~1.1% | No cap since 2024 |
| CO | FAMLI | 0.45% | SS wage base |
| CT | PFL | 0.50% | All wages |
| HI | TDI | 0.50% | $73,564 |
| MA | PFML | ~0.34% | SS wage base |
| NJ | TDI+FLI | ~0.37% | $41,400 |
| NY | DBL+PFL | ~0.87% | Varies |
| OR | PFML | ~0.36% EE share | SS wage base |
| RI | TDI | ~1.10% | $87,000 |
| WA | PFML | ~0.44% EE share | SS wage base |
| WA | WA Cares | 0.58% | All wages |

## Common Local Tax Jurisdictions
| Locality | State | Rate | Notes |
|----------|-------|------|-------|
| New York City | NY | 3.078-3.876% | Residents only; progressive |
| Yonkers | NY | 16.75% surcharge | On state tax |
| Philadelphia | PA | 3.75%/3.44% | Resident/non-resident |
| Pittsburgh | PA | $52/yr + ~3% EIT | LST + earned income |
| OH municipalities | OH | 1.0-2.5% | Credit for work city |
| Detroit | MI | 2.4%/1.2% | Resident/non-resident |
| Indianapolis | IN | ~2.02% | County tax |

## IT0210 State W-4 Forms
| State | Subtype | Form | Key Differences |
|-------|---------|------|-----------------|
| CA | 05 | DE 4 | Separate allowances; estimated deductions |
| NY | 33 | IT-2104 | Allowances; NYC/Yonkers status |
| IL | 14 | IL-W-4 | Basic/additional allowances; flat rate |
| PA | 39 | REV-419 | No allowances; flat rate |
| OH | 36 | IT-4 | Exemptions; school district |
| NJ | 31 | NJ-W4 | Filing status; wage chart |
| GA | 11 | G-4 | Allowances; personal credits |

## Tax Deposit Schedules
| Frequency | Rule |
|-----------|------|
| Semi-Weekly | >$50K liability in lookback period |
| Monthly | ≤$50K liability in lookback period |
| Next-Day | $100K+ undeposited at any point |

## Year-End Checklist
1. Apply final BSI tax update
2. Process year-end adjustments (GTL imputed income, fringe benefits)
3. Run preliminary W-2 totals (RPCTWNU0), reconcile to payroll register
4. Verify third-party sick pay, GTL imputed income, excess 401(k) deferrals
5. Generate W-2/W-3 files; submit by January 31
6. Generate state W-2 copies per state
7. Generate 1095-C for ACA (March deadline)
