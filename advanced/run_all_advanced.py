import time
from pathlib import Path

from advanced_agent import run_advanced


CASES = [f"case_{i:03d}" for i in range(1, 13)]

OUTPUT_DIR = Path("benchmark/predictions/advanced")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

run_times = []
overall_start = time.perf_counter()


for i, case_id in enumerate(CASES, start=1):

    print()
    print("=" * 60)
    print(f"Running advanced {i}/12: {case_id}")
    print("=" * 60)

    data_path = f"benchmark/cases/{case_id}/data.csv"
    output_path = OUTPUT_DIR / f"{case_id}.json"

    case_start = time.perf_counter()

    try:
        run_advanced(
            data_path=data_path,
            scenario_id=case_id,
            output_path=str(output_path),
        )

        elapsed = time.perf_counter() - case_start
        run_times.append(elapsed)

        print(f"Runtime: {elapsed:.2f} seconds")

    except Exception as e:

        elapsed = time.perf_counter() - case_start
        print(f"ERROR on {case_id}: {e}")
        print(f"Runtime before failure: {elapsed:.2f} seconds")

    time.sleep(2)


total_runtime = time.perf_counter() - overall_start
successful_runs = len(run_times)

print()
print("=" * 60)
print("ADVANCED RUN COMPLETE")
print("=" * 60)
print(f"Total runtime: {total_runtime:.2f} seconds")

if successful_runs:
    print(f"Average runtime/case: {sum(run_times) / successful_runs:.2f} seconds")
    print(f"Successful cases timed: {successful_runs}/12")