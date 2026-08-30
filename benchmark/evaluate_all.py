import json
from pathlib import Path

from evaluate import load_json, score_prediction


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

CASES = [f"case_{i:03d}" for i in range(1, 13)]

GROUND_TRUTH_DIR = Path("benchmark/cases")
PREDICTION_DIR = Path("benchmark/predictions/baseline")


# ---------------------------------------------------------
# Evaluate all baseline predictions
# ---------------------------------------------------------

results = []

for case_id in CASES:

    ground_truth_path = (
        GROUND_TRUTH_DIR
        / case_id
        / "ground_truth.json"
    )

    prediction_path = (
        PREDICTION_DIR
        / f"{case_id}.json"
    )

    if not prediction_path.exists():
        print(f"{case_id}: MISSING PREDICTION")
        continue

    ground_truth = load_json(
        ground_truth_path
    )

    prediction = load_json(
        prediction_path
    )

    result = score_prediction(
        ground_truth,
        prediction
    )

    results.append(result)

    status = (
        "CORRECT"
        if result["decision_correct"]
        else "INCORRECT"
    )

    print(
        f"{case_id}: {status}"
    )


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

total = len(results)

correct = sum(
    result["decision_correct"]
    for result in results
)

accuracy = (
    correct / total * 100
    if total > 0
    else 0
)

abstention_cases = [
    result
    for result in results
    if result["abstention_correct"] is not False
]

correct_abstentions = sum(
    result["abstention_correct"] is True
    for result in results
)

print()
print("=" * 50)
print("BASELINE EVALUATION SUMMARY")
print("=" * 50)

print(f"Cases evaluated: {total}")
print(f"Correct decisions: {correct}")
print(f"Incorrect decisions: {total - correct}")
print(f"Decision accuracy: {accuracy:.2f}%")
print(f"Correct abstentions: {correct_abstentions}")


# ---------------------------------------------------------
# Save complete results
# ---------------------------------------------------------

results_path = Path(
    "benchmark/predictions/baseline_results.json"
)

with open(results_path, "w") as f:
    json.dump(
        {
            "cases_evaluated": total,
            "correct_decisions": correct,
            "incorrect_decisions": total - correct,
            "decision_accuracy_pct": accuracy,
            "correct_abstentions": correct_abstentions,
            "results": results,
        },
        f,
        indent=4,
    )

print()
print(
    f"Results saved to: {results_path}"
)