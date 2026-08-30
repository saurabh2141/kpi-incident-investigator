import json
from pathlib import Path

from evaluate import load_json, score_prediction


correct = 0
results = []

for i in range(1, 13):
    case_id = f"case_{i:03d}"

    gt_path = Path(f"benchmark/cases/{case_id}/ground_truth.json")
    pred_path = Path(f"benchmark/predictions/advanced/{case_id}.json")

    gt = load_json(gt_path)
    pred = load_json(pred_path)

    result = score_prediction(gt, pred)
    results.append(result)

    if result["decision_correct"]:
        correct += 1

    print(
        case_id,
        "CORRECT" if result["decision_correct"] else "INCORRECT"
    )


accuracy = correct / 12 * 100

print()
print("=" * 40)
print("ADVANCED BENCHMARK RESULT")
print("=" * 40)
print(f"Correct: {correct}/12")
print(f"Decision Accuracy: {accuracy:.2f}%")

output = {
    "correct": correct,
    "total": 12,
    "decision_accuracy": accuracy,
    "results": results,
}

with open(
    "benchmark/predictions/advanced_results.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(output, f, indent=2)