#!/usr/bin/env python3
"""
SAP Payroll Plugin Test Harness — 50-run exhaustive validation
Tests the config workbook + migration file generation pipeline
across 50 synthetic companies in top 10 US industries + new industries.
v1.0: Companies now have benefits_approach, time_approach, and concurrent_employment fields.
"""

import json
import os
import re
import datetime

# ============================================================
# 50 COMPANY PROFILES — Expanded to 50 companies
# ============================================================

COMPANIES = [
    # === 1. HEALTHCARE (3 companies) ===
    {
        "id": 1, "code": "MHS", "name": "MountainView Health System",
        "industry": "Healthcare", "employees": 4500, "company_code": "1000",
        "pas": {"MHS1": "WA", "MHS2": "OR", "MHS3": "CA"},
        "psas": ["NURS", "ADMN", "PHYS", "TECH", "SUPP"],
        "ee_subgroups": {"S1": "Salaried Exempt", "H1": "Hourly Non-Exempt", "P1": "Physician", "N1": "Nursing", "T1": "Temp/PRN", "E1": "Executive"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["WA", "OR", "CA"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "HSA1", "LIFE", "STD1", "LTD1"],
        "wt_count": 42, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 2, "code": "PCH", "name": "Pacific Coast Hospital Group",
        "industry": "Healthcare", "employees": 2800, "company_code": "2000",
        "pas": {"PCH1": "CA", "PCH2": "NV"},
        "psas": ["CLIN", "ADMN", "EMER", "SURG"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "P1": "Physician", "N1": "Nurse", "T1": "Per Diem"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["CA", "NV"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "ROTH", "FSA1", "LIFE"],
        "wt_count": 45, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": True
    },
    {
        "id": 3, "code": "SMC", "name": "Southern Medical Centers Inc",
        "industry": "Healthcare", "employees": 1200, "company_code": "3000",
        "pas": {"SMC1": "TX", "SMC2": "FL"},
        "psas": ["CLIN", "ADMN", "LAB"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "P1": "Provider", "T1": "Temp"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["TX", "FL"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE"],
        "wt_count": 35, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 2. TECHNOLOGY (3 companies) ===
    {
        "id": 4, "code": "NXW", "name": "NexaWave Technologies",
        "industry": "Technology", "employees": 3200, "company_code": "1000",
        "pas": {"NXW1": "CA", "NXW2": "WA", "NXW3": "NY", "NXW4": "TX"},
        "psas": ["ENGR", "SALE", "ADMN", "EXEC", "SUPP"],
        "ee_subgroups": {"S1": "Salaried Exempt", "H1": "Hourly", "E1": "Executive", "C1": "Contractor", "I1": "Intern"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["CA", "WA", "NY", "TX"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "ROTH", "HSA1", "FSA1", "LIFE", "STD1", "LTD1"],
        "wt_count": 48, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 5, "code": "CLD", "name": "CloudPeak Software",
        "industry": "Technology", "employees": 800, "company_code": "1000",
        "pas": {"CLD1": "CO", "CLD2": "UT"},
        "psas": ["ENGR", "ADMN", "SALE"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "C1": "Contractor"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["CO", "UT"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "HSA1", "LIFE"],
        "wt_count": 32, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 6, "code": "QBT", "name": "QuantumBit AI Labs",
        "industry": "Technology", "employees": 500, "company_code": "1000",
        "pas": {"QBT1": "MA"},
        "psas": ["RSCH", "ENGR", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "E1": "Executive", "I1": "Intern"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["MA"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "ROTH", "HSA1", "LIFE", "STD1", "LTD1"],
        "wt_count": 38, "garnishments": False, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 3. MANUFACTURING (3 companies) ===
    {
        "id": 7, "code": "STE", "name": "SteelForge Industries",
        "industry": "Manufacturing", "employees": 5000, "company_code": "1000",
        "pas": {"STE1": "OH", "STE2": "PA", "STE3": "IN", "STE4": "MI"},
        "psas": ["PROD", "MAINT", "WHSE", "ADMN", "ENGR", "EXEC"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union Steel", "U2": "Union Maint", "E1": "Executive", "T1": "Temp"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["OH", "PA", "IN", "MI"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE", "STD1", "LTD1"],
        "wt_count": 52, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 8, "code": "APM", "name": "Apex Precision Manufacturing",
        "industry": "Manufacturing", "employees": 1800, "company_code": "2000",
        "pas": {"APM1": "IL", "APM2": "WI"},
        "psas": ["PROD", "ADMN", "WHSE", "QA"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union UAW", "T1": "Temp"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["IL", "WI"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 40, "garnishments": True, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 9, "code": "GRN", "name": "GreenTech Solar Manufacturing",
        "industry": "Manufacturing", "employees": 600, "company_code": "1000",
        "pas": {"GRN1": "AZ"},
        "psas": ["PROD", "ADMN", "ENGR"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "T1": "Temp"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["AZ"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "HSA1"],
        "wt_count": 30, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 4. FINANCIAL SERVICES (3 companies) ===
    {
        "id": 10, "code": "FPG", "name": "FirstPrime Financial Group",
        "industry": "Financial Services", "employees": 6000, "company_code": "1000",
        "pas": {"FPG1": "NY", "FPG2": "NJ", "FPG3": "CT", "FPG4": "FL"},
        "psas": ["BANK", "INVT", "ADMN", "COMP", "EXEC"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "E1": "Executive", "B1": "Banker", "A1": "Advisor"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["NY", "NJ", "CT", "FL"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "ROTH", "HSA1", "FSA1", "LIFE", "STD1", "LTD1"],
        "wt_count": 50, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 11, "code": "MWB", "name": "MidWest Bancorp",
        "industry": "Financial Services", "employees": 2200, "company_code": "1000",
        "pas": {"MWB1": "MO", "MWB2": "KS", "MWB3": "NE"},
        "psas": ["RETL", "COMM", "ADMN", "EXEC"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly (Teller)", "E1": "Executive"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["MO", "KS", "NE"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE", "STD1"],
        "wt_count": 38, "garnishments": True, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 12, "code": "SVB", "name": "SilverVault Insurance",
        "industry": "Financial Services", "employees": 1500, "company_code": "1000",
        "pas": {"SVB1": "GA", "SVB2": "NC"},
        "psas": ["UWRT", "CLMS", "ADMN", "SALE"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "A1": "Agent"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["GA", "NC"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE", "LTD1"],
        "wt_count": 35, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 5. RETAIL (3 companies) ===
    {
        "id": 13, "code": "URB", "name": "UrbanMart Retail Corp",
        "industry": "Retail", "employees": 8000, "company_code": "1000",
        "pas": {"URB1": "CA", "URB2": "TX", "URB3": "FL", "URB4": "NY", "URB5": "IL"},
        "psas": ["STOR", "DIST", "CORP", "EXEC"],
        "ee_subgroups": {"S1": "Salaried Mgr", "H1": "Hourly FT", "H2": "Hourly PT", "E1": "Executive", "T1": "Seasonal"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["CA", "TX", "FL", "NY", "IL"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE"],
        "wt_count": 45, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 14, "code": "FRV", "name": "FreshValue Grocers",
        "industry": "Retail", "employees": 3500, "company_code": "1000",
        "pas": {"FRV1": "OR", "FRV2": "WA", "FRV3": "ID"},
        "psas": ["STOR", "BAKE", "DELI", "WHSE", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union UFCW", "T1": "Seasonal"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["OR", "WA", "ID"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 40, "garnishments": True, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 15, "code": "LXF", "name": "LuxeFit Athleisure",
        "industry": "Retail", "employees": 1000, "company_code": "1000",
        "pas": {"LXF1": "CA", "LXF2": "NY"},
        "psas": ["STOR", "ECOM", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "T1": "Seasonal"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["CA", "NY"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "HSA1"],
        "wt_count": 33, "garnishments": False, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 6. ENERGY / UTILITIES (3 companies) ===
    {
        "id": 16, "code": "PWG", "name": "PowerGrid Energy Corp",
        "industry": "Energy", "employees": 7500, "company_code": "1000",
        "pas": {"PWG1": "TX", "PWG2": "OK", "PWG3": "LA", "PWG4": "NM"},
        "psas": ["OPER", "MAINT", "ENGR", "ADMN", "EXEC", "FIELD"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union IBEW", "U2": "Union USW", "E1": "Executive", "T1": "Contract"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["TX", "OK", "LA", "NM"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "ROTH", "HSA1", "LIFE", "STD1", "LTD1"],
        "wt_count": 55, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 17, "code": "SWE", "name": "SunWest Electric Coop",
        "industry": "Energy", "employees": 900, "company_code": "1000",
        "pas": {"SWE1": "AZ", "SWE2": "NV"},
        "psas": ["OPER", "ADMN", "FIELD"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union IBEW"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": True, "states": ["AZ", "NV"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE", "STD1"],
        "wt_count": 36, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 18, "code": "OFP", "name": "Offshore Petro Services",
        "industry": "Energy", "employees": 2000, "company_code": "1000",
        "pas": {"OFP1": "TX", "OFP2": "LA"},
        "psas": ["OFSH", "ONSH", "ADMN", "ENGR"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "R1": "Rotational", "T1": "Contract"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": False, "states": ["TX", "LA"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE", "STD1", "LTD1"],
        "wt_count": 42, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 7. CONSTRUCTION (3 companies) ===
    {
        "id": 19, "code": "TRC", "name": "Titan Roads & Construction",
        "industry": "Construction", "employees": 3000, "company_code": "1000",
        "pas": {"TRC1": "CA", "TRC2": "NV", "TRC3": "AZ"},
        "psas": ["HEVY", "ELEC", "PLMB", "ADMN", "PROJ"],
        "ee_subgroups": {"S1": "Salaried PM", "H1": "Hourly", "U1": "Union Laborers", "U2": "Union IBEW", "T1": "Day Labor"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["CA", "NV", "AZ"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 44, "garnishments": True, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 20, "code": "ARC", "name": "Archstone Builders Group",
        "industry": "Construction", "employees": 1500, "company_code": "1000",
        "pas": {"ARC1": "GA", "ARC2": "SC", "ARC3": "NC"},
        "psas": ["RESI", "COMM", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "T1": "Subcontractor"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": False, "states": ["GA", "SC", "NC"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 34, "garnishments": True, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 21, "code": "NWP", "name": "Northwest Plumbing & HVAC",
        "industry": "Construction", "employees": 400, "company_code": "1000",
        "pas": {"NWP1": "WA"},
        "psas": ["PLMB", "HVAC", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union UA", "A1": "Apprentice"},
        "payroll_areas": {"W1": "Weekly"},
        "unions": True, "states": ["WA"],
        "benefits": ["MED1", "DEN1", "401K"],
        "wt_count": 32, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 8. TRANSPORTATION / LOGISTICS (3 companies) ===
    {
        "id": 22, "code": "NTL", "name": "National TransLogistics",
        "industry": "Transportation", "employees": 10000, "company_code": "1000",
        "pas": {"NTL1": "TN", "NTL2": "TX", "NTL3": "OH", "NTL4": "CA", "NTL5": "IL"},
        "psas": ["DRIV", "WHSE", "DISP", "MECH", "ADMN", "EXEC"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "D1": "Driver OTR", "D2": "Driver Local", "U1": "Union Teamster", "T1": "Temp"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["TN", "TX", "OH", "CA", "IL"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "ROTH", "HSA1", "LIFE", "STD1", "LTD1"],
        "wt_count": 55, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 23, "code": "JFL", "name": "JetFreight Logistics",
        "industry": "Transportation", "employees": 2500, "company_code": "1000",
        "pas": {"JFL1": "KY", "JFL2": "IN", "JFL3": "GA"},
        "psas": ["AIRP", "GRND", "WHSE", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union IAM"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["KY", "IN", "GA"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE", "STD1"],
        "wt_count": 40, "garnishments": True, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 24, "code": "HBR", "name": "Harbor Marine Shipping",
        "industry": "Transportation", "employees": 700, "company_code": "1000",
        "pas": {"HBR1": "WA", "HBR2": "OR"},
        "psas": ["PORT", "OFFC", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union ILWU"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["WA", "OR"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 35, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 9. EDUCATION (3 companies) ===
    {
        "id": 25, "code": "STU", "name": "Summit University System",
        "industry": "Education", "employees": 5500, "company_code": "1000",
        "pas": {"STU1": "PA", "STU2": "NJ"},
        "psas": ["FACL", "STAF", "RSCH", "ADMN", "EXEC"],
        "ee_subgroups": {"S1": "Salaried Staff", "F1": "Faculty 9-Mo", "F2": "Faculty 12-Mo", "H1": "Hourly", "G1": "Grad Asst", "T1": "Adjunct"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["PA", "NJ"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "403B", "457B", "LIFE", "STD1", "LTD1", "TUTN"],
        "wt_count": 48, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": True
    },
    {
        "id": 26, "code": "KAS", "name": "KidStart Academy Schools",
        "industry": "Education", "employees": 1200, "company_code": "1000",
        "pas": {"KAS1": "FL", "KAS2": "GA"},
        "psas": ["TCHR", "ADMN", "SUPP"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "T1": "Substitute"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["FL", "GA"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 30, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 27, "code": "OLU", "name": "OnlineU EdTech Corp",
        "industry": "Education", "employees": 350, "company_code": "1000",
        "pas": {"OLU1": "CO"},
        "psas": ["ENGR", "CONT", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "C1": "Contractor", "I1": "Intern"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["CO"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "HSA1", "LIFE"],
        "wt_count": 32, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 10. HOSPITALITY (3 companies) ===
    {
        "id": 28, "code": "GHR", "name": "GrandHorizon Resorts",
        "industry": "Hospitality", "employees": 4000, "company_code": "1000",
        "pas": {"GHR1": "FL", "GHR2": "CA", "GHR3": "HI", "GHR4": "NV"},
        "psas": ["FRON", "FOOD", "HSKP", "ADMN", "EXEC"],
        "ee_subgroups": {"S1": "Salaried Mgr", "H1": "Hourly FT", "H2": "Hourly PT", "T1": "Seasonal", "E1": "Executive"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["FL", "CA", "HI", "NV"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE"],
        "wt_count": 46, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 29, "code": "BFC", "name": "BlueFin Cruise Lines",
        "industry": "Hospitality", "employees": 2000, "company_code": "1000",
        "pas": {"BFC1": "FL", "BFC2": "TX"},
        "psas": ["CREW", "OFFC", "PORT", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "M1": "Maritime", "T1": "Seasonal"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["FL", "TX"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE", "STD1"],
        "wt_count": 40, "garnishments": True, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 30, "code": "FSQ", "name": "FarmSquare Restaurant Group",
        "industry": "Hospitality", "employees": 600, "company_code": "1000",
        "pas": {"FSQ1": "OR", "FSQ2": "WA"},
        "psas": ["KITCH", "FRONT", "ADMN"],
        "ee_subgroups": {"S1": "Salaried Mgr", "H1": "Hourly", "T1": "Tipped", "P1": "Part-Time"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": False, "states": ["OR", "WA"],
        "benefits": ["MED1", "DEN1", "401K"],
        "wt_count": 35, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },

    # === 11. GOVERNMENT / PUBLIC SECTOR (2 companies) ===
    {
        "id": 31, "code": "CIT", "name": "City of Springfield Municipal",
        "industry": "Government", "employees": 3200, "company_code": "1000",
        "pas": {"CIT1": "IL"},
        "psas": ["FIRE", "POLIC", "DPUB", "ADMN", "PARKS"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union IAFF", "U2": "Union AFSCME"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["IL"],
        "benefits": ["MED1", "DEN1", "VIS1", "457B", "LIFE", "PENS"],
        "wt_count": 42, "garnishments": True, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "negative", "concurrent_employment": False
    },
    {
        "id": 32, "code": "STA", "name": "State Transportation Authority",
        "industry": "Government", "employees": 2100, "company_code": "1000",
        "pas": {"STA1": "CA"},
        "psas": ["MAINT", "OPER", "ADMN", "ENGR"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union UAPD"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": True, "states": ["CA"],
        "benefits": ["MED1", "DEN1", "VIS1", "457B", "PENS", "LIFE"],
        "wt_count": 38, "garnishments": True, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "third_party", "concurrent_employment": False
    },

    # === 12. NON-PROFIT (2 companies) ===
    {
        "id": 33, "code": "HUM", "name": "Humanity Works Foundation",
        "industry": "Non-Profit", "employees": 850, "company_code": "1000",
        "pas": {"HUM1": "NY", "HUM2": "MA"},
        "psas": ["PROG", "DEVEL", "ADMN", "FUND"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "C1": "Consultant"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["NY", "MA"],
        "benefits": ["MED1", "DEN1", "VIS1", "403B", "LIFE"],
        "wt_count": 28, "garnishments": False, "mid_year": False,
        "benefits_approach": "hybrid", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 34, "code": "CHD", "name": "ChildrenFirst Advocacy Alliance",
        "industry": "Non-Profit", "employees": 420, "company_code": "1000",
        "pas": {"CHD1": "TX"},
        "psas": ["CARE", "ADMN", "SUPP"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["TX"],
        "benefits": ["MED1", "DEN1", "403B", "LIFE"],
        "wt_count": 24, "garnishments": False, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "full", "concurrent_employment": False
    },

    # === 13. PHARMA / LIFE SCIENCES (2 companies) ===
    {
        "id": 35, "code": "BML", "name": "BioMed Labs Inc",
        "industry": "Pharma/Life Sciences", "employees": 2600, "company_code": "1000",
        "pas": {"BML1": "PA", "BML2": "NJ"},
        "psas": ["RSCH", "PROD", "QUAL", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "R1": "Researcher"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["PA", "NJ"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "HSA1", "LIFE", "STD1"],
        "wt_count": 46, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "third_party", "concurrent_employment": False
    },
    {
        "id": 36, "code": "GNX", "name": "GenexCorp Therapeutics",
        "industry": "Pharma/Life Sciences", "employees": 1850, "company_code": "1000",
        "pas": {"GNX1": "CA"},
        "psas": ["CLNC", "ADMN", "SALE", "SUPP"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "S2": "Sales Rep"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["CA"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "HSA1", "LIFE"],
        "wt_count": 40, "garnishments": False, "mid_year": False,
        "benefits_approach": "hybrid", "time_approach": "full", "concurrent_employment": False
    },

    # === 14. REAL ESTATE (2 companies) ===
    {
        "id": 37, "code": "KRT", "name": "KeyRent Property Management",
        "industry": "Real Estate", "employees": 320, "company_code": "1000",
        "pas": {"KRT1": "CO", "KRT2": "UT"},
        "psas": ["PROP", "MAINT", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["CO", "UT"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 26, "garnishments": False, "mid_year": True,
        "benefits_approach": "deductions_only", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 38, "code": "STR", "name": "Sterling Towers Development",
        "industry": "Real Estate", "employees": 580, "company_code": "1000",
        "pas": {"STR1": "NY", "STR2": "NJ", "STR3": "CT"},
        "psas": ["DEVEL", "CONST", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union Laborers"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["NY", "NJ", "CT"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 30, "garnishments": True, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "negative", "concurrent_employment": False
    },

    # === 15. AGRICULTURE (2 companies) ===
    {
        "id": 39, "code": "GRW", "name": "GreenAcres Farming Co",
        "industry": "Agriculture", "employees": 420, "company_code": "1000",
        "pas": {"GRW1": "IA", "GRW2": "IL"},
        "psas": ["CROP", "LIVE", "EQUIP", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "S1": "Seasonal"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": False, "states": ["IA", "IL"],
        "benefits": ["MED1", "DEN1", "401K"],
        "wt_count": 28, "garnishments": False, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "third_party", "concurrent_employment": False
    },
    {
        "id": 40, "code": "DAR", "name": "Dairy Alliance Resources",
        "industry": "Agriculture", "employees": 310, "company_code": "1000",
        "pas": {"DAR1": "WI", "DAR2": "MN"},
        "psas": ["PROD", "PROC", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly"},
        "payroll_areas": {"W1": "Weekly"},
        "unions": True, "states": ["WI", "MN"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 24, "garnishments": False, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "negative", "concurrent_employment": False
    },

    # === 16. MEDIA / ENTERTAINMENT (2 companies) ===
    {
        "id": 41, "code": "FLX", "name": "FlexStream Media Productions",
        "industry": "Media/Entertainment", "employees": 950, "company_code": "1000",
        "pas": {"FLX1": "CA"},
        "psas": ["PROD", "EDIT", "ADMN", "CREQ"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "C1": "Contractor"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["CA"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE"],
        "wt_count": 34, "garnishments": False, "mid_year": True,
        "benefits_approach": "full", "time_approach": "negative", "concurrent_employment": False
    },
    {
        "id": 42, "code": "BRD", "name": "Broadcast Network Alliance",
        "industry": "Media/Entertainment", "employees": 720, "company_code": "1000",
        "pas": {"BRD1": "NY", "BRD2": "GA"},
        "psas": ["NEWS", "PROD", "TECH", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union NABET"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": True, "states": ["NY", "GA"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE"],
        "wt_count": 32, "garnishments": True, "mid_year": False,
        "benefits_approach": "hybrid", "time_approach": "full", "concurrent_employment": False
    },

    # === 17. PROFESSIONAL SERVICES (2 companies) ===
    {
        "id": 43, "code": "AMR", "name": "Anchor & Mitchell Law Partners",
        "industry": "Professional Services", "employees": 280, "company_code": "1000",
        "pas": {"AMR1": "NY", "AMR2": "CA"},
        "psas": ["ATTY", "SUPP", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "P1": "Partner"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["NY", "CA"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "ROTH", "LIFE"],
        "wt_count": 36, "garnishments": False, "mid_year": False,
        "benefits_approach": "full", "time_approach": "third_party", "concurrent_employment": False
    },
    {
        "id": 44, "code": "BCG", "name": "Beacon Consulting Group",
        "industry": "Professional Services", "employees": 650, "company_code": "1000",
        "pas": {"BCG1": "TX", "BCG2": "CA", "BCG3": "IL"},
        "psas": ["CONS", "ANAL", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "C1": "Consultant"},
        "payroll_areas": {"B1": "Biweekly", "M1": "Monthly"},
        "unions": False, "states": ["TX", "CA", "IL"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "HSA1", "LIFE", "STD1"],
        "wt_count": 44, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "negative", "concurrent_employment": False
    },

    # === 18. TELECOMMUNICATIONS (2 companies) ===
    {
        "id": 45, "code": "STL", "name": "StellarComm Networks",
        "industry": "Telecommunications", "employees": 4800, "company_code": "1000",
        "pas": {"STL1": "TX", "STL2": "FL", "STL3": "CA"},
        "psas": ["TECH", "INST", "CUST", "ADMN", "EXEC"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union CWA", "T1": "Contract"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly", "M1": "Monthly"},
        "unions": True, "states": ["TX", "FL", "CA"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "ROTH", "HSA1", "LIFE", "STD1", "LTD1"],
        "wt_count": 48, "garnishments": True, "mid_year": True,
        "benefits_approach": "full", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 46, "code": "PLS", "name": "Pulse Wireless Solutions",
        "industry": "Telecommunications", "employees": 1200, "company_code": "1000",
        "pas": {"PLS1": "WA", "PLS2": "OR"},
        "psas": ["ENGR", "OPS", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "C1": "Contractor"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["WA", "OR"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "HSA1", "LIFE"],
        "wt_count": 38, "garnishments": False, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "full", "concurrent_employment": False
    },

    # === 19. AEROSPACE / DEFENSE (2 companies) ===
    {
        "id": 47, "code": "ADS", "name": "Apex Defense Systems",
        "industry": "Aerospace/Defense", "employees": 3400, "company_code": "1000",
        "pas": {"ADS1": "CA", "ADS2": "AZ"},
        "psas": ["MFNG", "ENGR", "QUAL", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union IAM", "C1": "Clearance"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["CA", "AZ"],
        "benefits": ["MED1", "MED2", "DEN1", "VIS1", "401K", "ROTH", "HSA1", "LIFE", "STD1", "LTD1"],
        "wt_count": 50, "garnishments": True, "mid_year": True,
        "benefits_approach": "hybrid", "time_approach": "full", "concurrent_employment": False
    },
    {
        "id": 48, "code": "AVE", "name": "AviationEdge Composites",
        "industry": "Aerospace/Defense", "employees": 890, "company_code": "1000",
        "pas": {"AVE1": "CO"},
        "psas": ["PROD", "ADMN", "ENGR"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "T1": "Temp"},
        "payroll_areas": {"B1": "Biweekly"},
        "unions": False, "states": ["CO"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "HSA1", "LIFE"],
        "wt_count": 36, "garnishments": False, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "third_party", "concurrent_employment": False
    },

    # === 20. FOOD & BEVERAGE MANUFACTURING (2 companies) ===
    {
        "id": 49, "code": "PST", "name": "PastaPerfect Manufacturing",
        "industry": "Food & Beverage", "employees": 650, "company_code": "1000",
        "pas": {"PST1": "MN"},
        "psas": ["PROD", "PKNG", "WHSE", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union UFCW"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["MN"],
        "benefits": ["MED1", "DEN1", "401K", "LIFE"],
        "wt_count": 32, "garnishments": True, "mid_year": False,
        "benefits_approach": "deductions_only", "time_approach": "negative", "concurrent_employment": False
    },
    {
        "id": 50, "code": "BEV", "name": "BeverageBrew Innovations",
        "industry": "Food & Beverage", "employees": 780, "company_code": "1000",
        "pas": {"BEV1": "CA", "BEV2": "CO"},
        "psas": ["BREW", "DIST", "ADMN"],
        "ee_subgroups": {"S1": "Salaried", "H1": "Hourly", "U1": "Union Teamster"},
        "payroll_areas": {"W1": "Weekly", "B1": "Biweekly"},
        "unions": True, "states": ["CA", "CO"],
        "benefits": ["MED1", "DEN1", "VIS1", "401K", "LIFE"],
        "wt_count": 34, "garnishments": False, "mid_year": True,
        "benefits_approach": "hybrid", "time_approach": "full", "concurrent_employment": False
    },
]


def get_company(run_id):
    """Get company profile for a given run ID (1-50)"""
    return COMPANIES[run_id - 1]


if __name__ == "__main__":
    print(f"=== {len(COMPANIES)} Company Profiles Loaded ===")
    print(f"\nIndustry Distribution:")
    industries = {}
    for c in COMPANIES:
        ind = c["industry"]
        industries[ind] = industries.get(ind, 0) + 1
    for ind, count in sorted(industries.items()):
        print(f"  {ind}: {count} companies")

    print(f"\nComplexity Range:")
    print(f"  Employees: {min(c['employees'] for c in COMPANIES)} - {max(c['employees'] for c in COMPANIES)}")
    print(f"  States: {min(len(c['states']) for c in COMPANIES)} - {max(len(c['states']) for c in COMPANIES)}")
    print(f"  PAs: {min(len(c['pas']) for c in COMPANIES)} - {max(len(c['pas']) for c in COMPANIES)}")
    print(f"  PSAs: {min(len(c['psas']) for c in COMPANIES)} - {max(len(c['psas']) for c in COMPANIES)}")
    print(f"  EE Subgroups: {min(len(c['ee_subgroups']) for c in COMPANIES)} - {max(len(c['ee_subgroups']) for c in COMPANIES)}")
    print(f"  Wage Types: {min(c['wt_count'] for c in COMPANIES)} - {max(c['wt_count'] for c in COMPANIES)}")
    print(f"  Union: {sum(1 for c in COMPANIES if c['unions'])} / {len(COMPANIES)}")
    print(f"  Garnishments: {sum(1 for c in COMPANIES if c['garnishments'])} / {len(COMPANIES)}")
    print(f"  Mid-Year: {sum(1 for c in COMPANIES if c['mid_year'])} / {len(COMPANIES)}")

    print(f"\nBenefits Approach Distribution:")
    benefits_approaches = {}
    for c in COMPANIES:
        ba = c.get("benefits_approach", "unknown")
        benefits_approaches[ba] = benefits_approaches.get(ba, 0) + 1
    for ba, count in sorted(benefits_approaches.items()):
        print(f"  {ba}: {count} companies")

    print(f"\nTime Approach Distribution:")
    time_approaches = {}
    for c in COMPANIES:
        ta = c.get("time_approach", "unknown")
        time_approaches[ta] = time_approaches.get(ta, 0) + 1
    for ta, count in sorted(time_approaches.items()):
        print(f"  {ta}: {count} companies")

    print(f"\nConcurrent Employment: {sum(1 for c in COMPANIES if c.get('concurrent_employment', False))} / {len(COMPANIES)}")
