import time
from pathlib import Path

from baseline_agent import run_baseline


CASES = [f"case_{i:03d}" for i in range(1, 13)]

OUTPUT_DIR = Path("benchmark/predictions/baseline")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


for i, case_id in enumerate(CASES, start=1):

    print()
    print("=" * 60)
    print(f"Running baseline {i}/12: {case_id}")
    print("=" * 60)

    data_path = (
        f"benchmark/cases/{case_id}/data.csv"
    )

    output_path = (
        OUTPUT_DIR / f"{case_id}.json"
    )

    try:
        run_baseline(
            data_path=data_path,
            scenario_id=case_id,
            output_path=str(output_path),
        )

    except Exception as e:

        print(f"ERROR on {case_id}: {e}")

    # Small pause to be gentle with free-tier rate limits
    time.sleep(2)


print()
print("=" * 60)
print("BASELINE RUN COMPLETE")
print("=" * 60)