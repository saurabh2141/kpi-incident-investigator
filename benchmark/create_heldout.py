import json
from pathlib import Path
from generate_benchmark import (
    generate_base_data,
    inject_price_drop,
    inject_traffic_drop,
)

root = Path("benchmark") / "heldout"
root.mkdir(parents=True, exist_ok=True)

cases = [
    {
        "case_id": "heldout_001",
        "seed": 202701,
        "inject": "price",
        "region": "North",
        "product": "Clothing",
    },
    {
        "case_id": "heldout_002",
        "seed": 202702,
        "inject": "traffic",
        "region": "South",
        "product": "Electronics",
    },
]

for case in cases:
    case_dir = root / case["case_id"]
    case_dir.mkdir(parents=True, exist_ok=True)

    df = generate_base_data(seed=case["seed"])

    if case["inject"] == "price":
        df, impact = inject_price_drop(
            df=df,
            region=case["region"],
            product=case["product"],
            multiplier=0.80,
        )
        cause = "price_drop"

    else:
        df, impact = inject_traffic_drop(
            df=df,
            region=case["region"],
            product=case["product"],
            multiplier=0.60,
        )
        cause = "traffic_drop"

    data_path = case_dir / "data.csv"
    truth_path = case_dir / "ground_truth.json"

    df.to_csv(data_path, index=False)

    ground_truth = {
        "scenario_id": case["case_id"],
        "scenario_type": "heldout_validation",
        "target_kpi": "revenue",
        "direction": "decrease",
        "dominant_cause": cause,
        "affected_region": case["region"],
        "affected_product": case["product"],
        "should_abstain": False,
        "expected_impact": impact,
    }

    with open(truth_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=4)

    print(f"{case['case_id']} created")
    print(f"  cause: {cause}")
    print(f"  segment: {case['region']} / {case['product']}")
    print(f"  impact: {impact:.2f}")

print("Held-out validation cases created.")
