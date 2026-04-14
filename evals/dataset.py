# evals/dataset.py

# New claim inputs — these are what the agent receives at runtime
# Each maps to exactly one weather_data.json entry via incident_date + incident_location
# Restricted to 5 inputs: 2 failure mode cases, 1 repeat claims case,
# 1 clean baseline, 1 live unscripted case

CLAIM_INPUTS = [

    # --- FAILURE MODE: tool selection (agent skips weather check) ---
    {
        "claim_id": "CLAIM-2024-0891",
        "claimant_id": "CLM007",
        "property_id": "PROP007",
        "incident_date": "2024-06-15",          # → Amsterdam 2024-06-15 (38.2mm, below threshold)
        "incident_location": "Amsterdam",
        "damage_type": "water_damage",
        "reported_cause": "Burst pipe following sudden pressure drop in main supply line",
        "estimated_amount_eur": 28900,
        "reported_by": "Facilities Manager",
        "days_since_discovery": 3,
        "contractor_work_recent": False
    },

    # --- FAILURE MODE: overconfident recommendation on ambiguous claim ---
    {
        "claim_id": "CLAIM-2024-0312",
        "claimant_id": "CLM005",
        "property_id": "PROP005",
        "incident_date": "2024-03-11",          # → Amsterdam 2024-03-11 (39.1mm, 88km/h — both just below)
        "incident_location": "Amsterdam",
        "damage_type": "water_damage",
        "reported_cause": "Water ingress through roof following heavy rain. Roof repair completed 2024-02-20.",
        "estimated_amount_eur": 9400,
        "reported_by": "Building Supervisor",
        "days_since_discovery": 1,
        "contractor_work_recent": True
    },

    # --- REPEAT CLAIMS: triggers Clause 5, high value, weather supported ---
    {
        "claim_id": "CLAIM-2024-0156",
        "claimant_id": "CLM001",
        "property_id": "PROP001",
        "incident_date": "2024-09-22",          # → Amsterdam 2024-09-22 (52.1mm, above threshold)
        "incident_location": "Amsterdam",
        "damage_type": "water_damage",
        "reported_cause": "Flooding in basement following heavy rainfall. Third incident at this property.",
        "estimated_amount_eur": 31400,
        "reported_by": "Property Manager",
        "days_since_discovery": 2,
        "contractor_work_recent": False
    },

    # --- CLEAN BASELINE: no prior history, straightforward damage ---
    {
        "claim_id": "CLAIM-2022-0441",
        "claimant_id": "CLM003",
        "property_id": "PROP003",
        "incident_date": "2022-08-03",          # → Utrecht 2022-08-03 (8.2mm, no weather event)
        "incident_location": "Utrecht",
        "damage_type": "water_damage",
        "reported_cause": "Burst pipe in utility room. No prior incidents at this property.",
        "estimated_amount_eur": 9800,
        "reported_by": "Tenant",
        "days_since_discovery": 1,
        "contractor_work_recent": False
    },

    # --- LIVE UNSCRIPTED: clean claimant, ambiguous cause, run live during workshop ---
    {
        "claim_id": "CLAIM-2024-1103",
        "claimant_id": "CLM006",
        "property_id": "PROP006",
        "incident_date": "2024-11-03",          # → Amsterdam 2024-11-03 (22.4mm, no weather event)
        "incident_location": "Amsterdam",
        "damage_type": "water_damage",
        "reported_cause": "Tenant noticed water pooling under kitchen units. Source unclear.",
        "estimated_amount_eur": 14200,
        "reported_by": "Property Manager",
        "days_since_discovery": 1,
        "contractor_work_recent": False
    },
]

# Expected outputs — to be completed after agent is built
# Tool call sequences follow this convention:
# ["search_policy_docs", "query_weather_data", "query_claims_history", "retrieve_repair_estimate"]
# Coverage decisions: "covered" | "partial" | "excluded"
# Settlement recommendations: "auto_settle" | "assign_adjuster" | "flag_for_investigation"
# Confidence levels: "high" | "medium" | "low"

EXPECTED_OUTPUTS = [
    {
        "claim_id": "CLAIM-2024-0891",
        "expected_tool_calls": [],        # fill in after agent build
        "expected_coverage_decision": "", # fill in after agent build
        "expected_settlement": "",        # fill in after agent build
        "expected_confidence": "",        # fill in after agent build
    },
    {
        "claim_id": "CLAIM-2024-0312",
        "expected_tool_calls": [],
        "expected_coverage_decision": "",
        "expected_settlement": "",
        "expected_confidence": "",
    },
    {
        "claim_id": "CLAIM-2024-0156",
        "expected_tool_calls": [],
        "expected_coverage_decision": "",
        "expected_settlement": "",
        "expected_confidence": "",
    },
    {
        "claim_id": "CLAIM-2022-0441",
        "expected_tool_calls": [],
        "expected_coverage_decision": "",
        "expected_settlement": "",
        "expected_confidence": "",
    },
    {
        "claim_id": "CLAIM-2024-1103",
        "expected_tool_calls": [],
        "expected_coverage_decision": "",
        "expected_settlement": "",
        "expected_confidence": "",
    },
]