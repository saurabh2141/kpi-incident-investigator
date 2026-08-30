import argparse
import json
from pathlib import Path


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize(value):
    """
    Normalize strings so capitalization and spacing do not
    affect deterministic scoring.
    """
    if value is None:
        return None

    if isinstance(value, str):
        return value.strip().lower().replace(" ", "_")

    return value


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------
# Main scorer
# ---------------------------------------------------------

def score_prediction(ground_truth, prediction):
    """
    Compare one structured agent prediction against
    the benchmark ground truth.

    Primary metric:
        Decision Correct = 1 or 0

    For dominant-cause cases:
        the system must not abstain and must identify:
        - cause
        - region
        - product

    For abstention cases:
        the system must correctly abstain.
    """

    result = {
        "scenario_id": ground_truth["scenario_id"],
        "decision_correct": False,
        "abstention_correct": False,
        "cause_correct": None,
        "region_correct": None,
        "product_correct": None,
        "impact_error_pct": None,
    }

    gt_should_abstain = ground_truth.get(
        "should_abstain",
        False
    )

    pred_should_abstain = prediction.get(
        "should_abstain",
        False
    )

    # -----------------------------------------------------
    # Abstention cases
    # -----------------------------------------------------

    if gt_should_abstain:

        result["abstention_correct"] = (
            pred_should_abstain is True
        )

        result["decision_correct"] = (
            pred_should_abstain is True
        )

        return result

    # -----------------------------------------------------
    # Dominant-cause cases
    # -----------------------------------------------------

    if pred_should_abstain:
        # Ground truth has a dominant cause but agent abstained.
        return result

    gt_cause = normalize(
        ground_truth.get("dominant_cause")
    )

    pred_cause = normalize(
        prediction.get("dominant_cause")
    )

    gt_region = normalize(
        ground_truth.get("affected_region")
    )

    pred_region = normalize(
        prediction.get("affected_region")
    )

    gt_product = normalize(
        ground_truth.get("affected_product")
    )

    pred_product = normalize(
        prediction.get("affected_product")
    )

    result["cause_correct"] = (
        pred_cause == gt_cause
    )

    result["region_correct"] = (
        pred_region == gt_region
    )

    result["product_correct"] = (
        pred_product == gt_product
    )

    result["decision_correct"] = all(
        [
            result["cause_correct"],
            result["region_correct"],
            result["product_correct"],
        ]
    )

    # -----------------------------------------------------
    # Optional impact estimation scoring
    # -----------------------------------------------------

    expected_impact = ground_truth.get(
        "expected_impact"
    )

    estimated_impact = prediction.get(
        "estimated_impact"
    )

    if (
        expected_impact is not None
        and estimated_impact is not None
        and expected_impact != 0
    ):

        result["impact_error_pct"] = abs(
            estimated_impact - expected_impact
        ) / abs(expected_impact) * 100

    return result


# ---------------------------------------------------------
# Command line interface
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Deterministically score a KPI incident "
            "investigator prediction."
        )
    )

    parser.add_argument(
        "--ground-truth",
        required=True,
        help="Path to ground_truth.json",
    )

    parser.add_argument(
        "--prediction",
        required=True,
        help="Path to prediction.json",
    )

    args = parser.parse_args()

    ground_truth = load_json(
        Path(args.ground_truth)
    )

    prediction = load_json(
        Path(args.prediction)
    )

    result = score_prediction(
        ground_truth,
        prediction
    )

    print()
    print("EVALUATION RESULT")
    print("-----------------")
    print(json.dumps(result, indent=4))

    if result["decision_correct"]:
        print()
        print("PRIMARY DECISION: CORRECT")
    else:
        print()
        print("PRIMARY DECISION: INCORRECT")


if __name__ == "__main__":
    main()