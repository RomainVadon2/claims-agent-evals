"""
Data loaders — parse each source file and return clean Python objects.

In production these functions would call external APIs. For the workshop
they read local fixture files with the same return structure.
"""

import csv
import json
from pathlib import Path

SOURCES = Path(__file__).parent / "sources"


def load_policy_docs() -> str:
    """Return the full policy document as plain text for LLM reasoning."""
    return (SOURCES / "policy_docs.md").read_text()


def load_claims_history(claimant_id: str) -> list[dict]:
    """Return all prior claims for a given claimant."""
    history = []
    with open(SOURCES / "claims_history.csv", newline="") as f:
        for row in csv.DictReader(f):
            if row["claimant_id"] == claimant_id:
                history.append({
                    "claim_id": row["claim_id"],
                    "claim_date": row["claim_date"],
                    "damage_type": row["damage_type"],
                    "amount_eur": int(row["amount_eur"]),
                    "outcome": row["outcome"],
                    "prior_defect_documented": row["prior_defect_documented"] == "true",
                    "defect_date": row["defect_date"] or None,
                    "notes": row["notes"],
                })
    if not history:
        return [{"notes": f"No prior claims found for claimant {claimant_id}."}]
    return history


def load_weather_data(incident_date: str, location: str) -> dict:
    """Return historical weather record for a given date and location."""
    data = json.loads((SOURCES / "weather_data.json").read_text())
    result = data.get(location, {}).get(incident_date, {})
    if not result:
        return {
            "precipitation_mm": None,
            "wind_kmh": None,
            "conditions": "Unknown",
            "notes": f"No weather data available for {location} on {incident_date}.",
        }
    return result


def load_repair_estimate(claim_id: str) -> dict:
    """Parse the repair estimates document and return the section for a given claim."""
    text = (SOURCES / "repair_estimates.md").read_text()

    sections = text.split("\n---\n")
    for section in sections:
        if f"## {claim_id}" in section:
            total = None
            conclusion_lines = []
            in_conclusion = False

            for line in section.splitlines():
                if line.startswith("**Total Estimate:**"):
                    total = line.replace("**Total Estimate:**", "").strip()
                if line.startswith("**Conclusion:**"):
                    in_conclusion = True
                    first = line.replace("**Conclusion:**", "").strip()
                    if first:
                        conclusion_lines.append(first)
                elif in_conclusion:
                    if line.startswith("**") or line.startswith("---"):
                        break
                    if line.strip():
                        conclusion_lines.append(line.strip())

            return {
                "claim_id": claim_id,
                "total_estimate": total,
                "conclusion": " ".join(conclusion_lines),
                "full_text": section.strip(),
            }

    return {
        "claim_id": claim_id,
        "total_estimate": None,
        "conclusion": None,
        "full_text": f"No repair estimate found for claim {claim_id}.",
    }
