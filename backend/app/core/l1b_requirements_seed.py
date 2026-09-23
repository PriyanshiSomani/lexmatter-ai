"""
LexMatter AI — Official L-1B Legal Framework Seed Data
Contains legal authorities (8 CFR 214.2(l), USCIS Policy Manual) and Requirements R1-R6 with evaluation dimensions.
"""

from datetime import date
from typing import Any, Dict, List

# Official Legal Authorities
AUTHORITIES_SEED: List[Dict[str, Any]] = [
    {
        "id": "auth_8cfr_214_2_l",
        "authority_type": "REGULATION",
        "citation_title": "8 CFR 214.2(l)(1)(ii)(D) — Intracompany Transferee Specialized Knowledge",
        "jurisdiction": "US_FEDERAL",
        "source_url": "https://www.ecfr.gov/current/title-8/chapter-I/subchapter-B/part-214/section-214.2#p-214.2(l)(1)(ii)(D)",
        "full_text": "Specialized knowledge means special knowledge possessed by an individual of the petitioning organization's product, service, research, equipment, techniques, management, or other interests and its application in international markets, or an advanced level of knowledge or expertise in the organization's processes and procedures.",
        "effective_date": date(2015, 8, 17),
    },
    {
        "id": "auth_uscis_pm_vol2_l",
        "authority_type": "USCIS_POLICY_MANUAL",
        "citation_title": "USCIS Policy Manual Volume 2, Part L — L-1 Intracompany Transferees",
        "jurisdiction": "US_FEDERAL",
        "source_url": "https://www.uscis.gov/policy-manual/volume-2-part-l",
        "full_text": "To qualify for L-1 classification, the petitioner must demonstrate a qualifying foreign relationship, active doing of business in both locations, 1 year of continuous foreign employment within the prior 3 years, and that the beneficiary possesses specialized knowledge required for the U.S. position.",
        "effective_date": date(2020, 1, 1),
    },
]

# Requirements R1 through R6 with Evaluation Dimensions
REQUIREMENTS_SEED: List[Dict[str, Any]] = [
    {
        "code": "L1B-REQ-R1",
        "case_type": "L1B",
        "category": "ELIGIBILITY",
        "title": "Qualifying Foreign Organization & Corporate Relationship",
        "version_number": 1,
        "authority_id": "auth_uscis_pm_vol2_l",
        "description": "The U.S. petitioning entity must have a qualifying relationship with the foreign employer (parent company, branch, subsidiary, or affiliate).",
        "evaluation_dimensions": [
            "qualifying_foreign_entity_exists",
            "qualifying_us_entity_exists",
            "qualifying_corporate_ownership_relationship",
        ],
    },
    {
        "code": "L1B-REQ-R2",
        "case_type": "L1B",
        "category": "ELIGIBILITY",
        "title": "Doing Business (United States and Foreign Location)",
        "version_number": 1,
        "authority_id": "auth_uscis_pm_vol2_l",
        "description": "The petitioner must be doing business as an employer in the United States and at least one foreign country directly or through an affiliate for the duration of the beneficiary's stay.",
        "evaluation_dimensions": [
            "active_business_us",
            "active_business_foreign",
            "regular_systematic_provision_of_goods_or_services",
        ],
    },
    {
        "code": "L1B-REQ-R3",
        "case_type": "L1B",
        "category": "ELIGIBILITY",
        "title": "One Year Continuous Foreign Employment Within Prior Three Years",
        "version_number": 1,
        "authority_id": "auth_8cfr_214_2_l",
        "description": "The beneficiary must have been employed abroad continuously for one full year within the three years immediately preceding the filing of the petition.",
        "evaluation_dimensions": [
            "qualifying_foreign_employer",
            "continuous_one_year_duration",
            "within_prior_three_years_window",
            "qualifying_capacity_executive_managerial_or_specialized",
        ],
    },
    {
        "code": "L1B-REQ-R4",
        "case_type": "L1B",
        "category": "ELIGIBILITY",
        "title": "Specialized Knowledge Standard (Proprietary or Advanced)",
        "version_number": 1,
        "authority_id": "auth_8cfr_214_2_l",
        "description": "The beneficiary must possess specialized knowledge—either special knowledge of the organization's product/service or an advanced level of expertise in processes/procedures.",
        "evaluation_dimensions": [
            "proprietary_product_process_or_system",
            "advanced_expertise_level",
            "organizational_or_industry_comparison",
            "beneficiary_possession_evidence",
        ],
    },
    {
        "code": "L1B-REQ-R5",
        "case_type": "L1B",
        "category": "ELIGIBILITY",
        "title": "Proposed U.S. Position Duties and Specialized Knowledge Need",
        "version_number": 1,
        "authority_id": "auth_uscis_pm_vol2_l",
        "description": "The proposed position in the United States must require specialized knowledge and involve duties consistent with that capacity.",
        "evaluation_dimensions": [
            "us_position_duties_described",
            "specialized_knowledge_required_for_role",
            "alignment_with_foreign_experience",
        ],
    },
    {
        "code": "L1B-REQ-R6",
        "case_type": "L1B",
        "category": "EVIDENTIARY",
        "title": "Beneficiary Qualifications, Education, and Training Records",
        "version_number": 1,
        "authority_id": "auth_uscis_pm_vol2_l",
        "description": "Supporting evidence must demonstrate that the beneficiary's education, prior training, and experience qualify them to hold the specialized knowledge role.",
        "evaluation_dimensions": [
            "education_records_present",
            "training_certificates_or_internal_records",
            "prior_project_or_product_contributions",
        ],
    },
]
