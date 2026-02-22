# Payroll Interfaces Reference

## Standard SAP Payroll Interfaces

### Outbound Interfaces

#### IF-01: FI Posting (RPCIPTU0)
- **Direction**: SAP Payroll → SAP FI/CO
- **Program**: RPCIPTU0
- **Format**: Internal SAP posting
- **Frequency**: Per payroll run
- **Details**: See fi-posting.md for full configuration

#### IF-02: Bank Transfer / ACH (RFFOUS_T)
- **Direction**: SAP Payroll → Bank
- **Program**: RFFOUS_T
- **Format**: NACHA CCD+/PPD+ (balanced file)
- **Frequency**: Per payroll run
- **Key Config**: House bank (T012), payment method T
- **File Naming**: COMPANY_ACH_YYYYMMDD_nn.txt
- **Protocol**: SFTP to bank

#### IF-03: Positive Pay
- **Direction**: SAP → Bank
- **Program**: Custom ABAP (or standard if available)
- **Format**: Bank-specific fixed-width
- **Frequency**: Per payroll run (checks only)
- **Purpose**: Fraud prevention — bank verifies check issuance
- **File Naming**: COMPANY_POSITIVEPAY_YYYYMMDD.txt

#### IF-04: Tax Filing
- **Direction**: SAP → Tax Filing Service (ADP SmartCompliance, Ceridian, etc.)
- **Program**: RPCTAXU0 (extract) + filing service format
- **Format**: Service-specific proprietary format
- **Frequency**: Quarterly (941) + Annual (W-2/W-3)
- **Content**: Payroll totals by tax authority, employee W-2 data
- **Key Programs**: RPCTWNU0 (W-2 generation), RPCTAXU0 (tax reporting)

#### IF-05: 401(k) / Retirement
- **Direction**: SAP → Plan Administrator (Fidelity, Vanguard, etc.)
- **Format**: Plan sponsor CSV or fixed-width (provider-specific)
- **Frequency**: Per payroll run
- **Content**: EE contributions, ER match, loan repayments, catch-up
- **File Naming**: COMPANY_401K_YYYYMMDD.csv

#### IF-06: Benefits Carrier Files
- **Direction**: SAP → Insurance Carriers
- **Format**: ANSI 834 EDI (standard) or carrier-specific
- **Frequency**: Monthly (or per enrollment event)
- **Content**: Enrollment data, coverage levels, effective dates
- **File Naming**: COMPANY_834_CARRIER_YYYYMM.edi

#### IF-07: Workers Compensation
- **Direction**: SAP → WC Insurance Carrier
- **Format**: Custom CSV
- **Frequency**: Quarterly
- **Content**: Hours and earnings by WC class code per employee
- **File Naming**: COMPANY_WC_YYYYQQ.csv

### Inbound Interfaces

#### IF-08: Time Data Import
- **Direction**: Time System (Kronos, ADP, etc.) → SAP
- **Method**: CATS BAPI (BAPI_CATIMESHEETMGR_INSERT) or flat file via LSMW
- **Format**: BAPI call (real-time) or CSV/XML batch
- **Frequency**: Daily (batch) or real-time
- **Target ITs**: IT2001 (Absences), IT2002 (Attendances), IT2003 (Substitutions)
- **Error Handling**: Error log in SM37; retry queue

#### IF-09: New Hire Data
- **Direction**: Recruiting/Onboarding System → SAP
- **Method**: SAP PI/PO middleware, BAPI, or IDoc
- **Format**: SAP Integration (event-driven)
- **Frequency**: As needed (new hire events)
- **Target**: PA40 (Hire action) creating IT0000-0008, IT0207, IT0208, IT0210

#### IF-10: Benefits Elections
- **Direction**: Benefits Platform → SAP
- **Method**: SAP PI/PO or direct integration
- **Format**: SAP Integration
- **Frequency**: Open enrollment + life events
- **Target ITs**: IT0167/0168 (benefit plan enrollment/deductions)

## Interface Design Patterns

### File-Based Interfaces
```
Source System → File Generation → SFTP Transfer → SAP (or External)
                                       ↓
                              Error/Confirmation File
```

### BAPI-Based Interfaces
```
Source System → Middleware (PI/PO) → BAPI Call → SAP Infotype Update
                                        ↓
                               Return Code / Error Log
```

### Key Design Decisions
1. **Frequency**: Real-time (BAPI) vs. batch (file) — driven by business need
2. **Error handling**: Retry queue, error notification, manual correction process
3. **File naming**: Include company ID, interface type, date, sequence number
4. **Archiving**: Retain interface files for audit trail (per retention policy)
5. **Monitoring**: SM37 (job log), SLG1 (application log), or custom monitoring

## Common Interface Programs
| Program | Purpose |
|---------|---------|
| RFFOUS_T | ACH bank transfer (US) |
| RPCIPTU0 | FI posting |
| RPCTAXU0 | Tax reporting extract |
| RPCTWNU0 | W-2 generation |
| RPCEDTU0 | Remuneration statement (pay slip) |
| RPCLJNU0 | Payroll journal |
| RPTIME00 | Time evaluation |
| CATS_DA | CATS data approval |
