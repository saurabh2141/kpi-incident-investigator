import json
from pathlib import Path

from generate_benchmark import generate_base_data


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

# This seed intentionally produces a modest natural
# post-Aug-15 revenue decline from normal variation.
SEED = 500
INCIDENT_START = "2026-08-15"

OUTPUT_DIR = Path("benchmark/cases/case_012")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Generate normal business data
# ---------------------------------------------------------
# IMPORTANT:
# We do NOT inject any actual revenue-causing incident.
# Any observed revenue movement comes from normal
# variation in the synthetic data.
# ---------------------------------------------------------

df = generate_base_data(seed=SEED)


# ---------------------------------------------------------
# MISLEADING SIGNAL
# ---------------------------------------------------------
# Marketing spend drops dramatically in North / Electronics
# after Aug 15.
#
# However, in this benchmark generator, marketing_spend
# does NOT mechanically determine visitors or orders.
#
# Therefore this is a temporal correlation, not a known
# causal mechanism for the revenue movement.
# ---------------------------------------------------------

marketing_mask = (
    (df["date"] >= INCIDENT_START)
    & (df["region"] == "North")
    & (df["product"] == "Electronics")
)

df.loc[
    marketing_mask,
    "marketing_spend"
] *= 0.30


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

data_path = OUTPUT_DIR / "data.csv"

df.to_csv(
    data_path,
    index=False
)


# ---------------------------------------------------------
# Save ground truth
# ---------------------------------------------------------

ground_truth = {
    "scenario_id": "case_012",
    "scenario_type": "noise_only_with_red_herring",

    "user_question": (
        "Why did overall revenue drop after 2026-08-15?"
    ),

    "target_kpi": "revenue",
    "direction": "decrease",

    # There is deliberately no injected causal incident.
    "dominant_cause": None,
    "should_abstain": True,

    "expected_behavior": (
        "Recognize that the available evidence does not "
        "support a dominant root cause. Do not attribute "
        "the revenue movement to marketing merely because "
        "marketing changed during the same period."
    ),

    "red_herrings": [
        {
            "type": "marketing_spend_drop",
            "region": "North",
            "product": "Electronics",
            "reason_not_causal": (
                "Marketing spend is not connected to visitor "
                "generation in the synthetic data-generating "
                "process."
            ),
        }
    ],

    # No causal revenue impact was injected.
    "total_expected_impact": 0.0,

    "incident_start": INCIDENT_START,
    "random_seed": SEED,
}


ground_truth_path = OUTPUT_DIR / "ground_truth.json"

with open(ground_truth_path, "w") as f:
    json.dump(
        ground_truth,
        f,
        indent=4
    )


print("Case 012 generated successfully.")
print(f"Dataset saved to: {data_path}")
print(f"Ground truth saved to: {ground_truth_path}")
print("Injected causal revenue impact: 0.00")
print("Correct behavior: ABSTAIN")