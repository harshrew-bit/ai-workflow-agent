#!/usr/bin/env bash
# run_examples.sh — Execute benchmark example requests offline and verify against expected.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_DIR}"

# Select Python executable
if [ -f "${REPO_DIR}/.venv/bin/python" ]; then
    PYTHON_BIN="${REPO_DIR}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

OUTPUT_DIR="${REPO_DIR}/examples/output"
EXPECTED_FILE="${REPO_DIR}/examples/expected.json"

mkdir -p "${OUTPUT_DIR}"

if [ ! -f "${EXPECTED_FILE}" ]; then
    echo "ERROR: Expected file not found at ${EXPECTED_FILE}" >&2
    exit 1
fi

echo "========================================================================"
echo " Running AI Workflow Agent Benchmark Suite (Offline Mode)"
echo " Python: ${PYTHON_BIN}"
echo " Target: ${OUTPUT_DIR}"
echo "========================================================================"

FAILED_COUNT=0
PASSED_COUNT=0

# Use Python runner helper to execute, verify, and write artifacts reliably
"${PYTHON_BIN}" - << 'EOF'
import json
import subprocess
import sys
from pathlib import Path

repo_dir = Path.cwd()
expected_file = repo_dir / "examples" / "expected.json"
output_dir = repo_dir / "examples" / "output"
output_dir.mkdir(parents=True, exist_ok=True)

with open(expected_file, "r", encoding="utf-8") as f:
    expected_data = json.load(f)

failures = []
passed = 0

print(f"Loaded {len(expected_data)} benchmark test case(s)...\n")

for slug, spec in expected_data.items():
    request_text = spec["request"]
    exp_wf = spec["expected_workflow_id"]
    exp_status = spec["expected_status"]
    exp_exit = spec["expected_exit_code"]

    txt_out_file = output_dir / f"{slug}.txt"
    json_out_file = output_dir / f"{slug}.json"

    # 1. Run text report
    env_clean = {k: v for k, v in subprocess.os.environ.items() if "API_KEY" not in k and k != "LLM_PROVIDER"}

    proc_txt = subprocess.run(
        [sys.executable, "-m", "app.main", request_text],
        capture_output=True,
        text=True,
        env=env_clean,
    )
    with open(txt_out_file, "w", encoding="utf-8") as f:
        f.write(proc_txt.stdout)

    # 2. Run JSON report
    proc_json = subprocess.run(
        [sys.executable, "-m", "app.main", "--json", request_text],
        capture_output=True,
        text=True,
        env=env_clean,
    )
    with open(json_out_file, "w", encoding="utf-8") as f:
        f.write(proc_json.stdout)

    actual_exit = proc_json.returncode

    # 3. Parse JSON output and verify contracts
    try:
        report_data = json.loads(proc_json.stdout)
    except Exception as exc:
        failures.append((slug, f"Failed to parse JSON output: {exc}"))
        print(f"[FAIL] {slug:<28} | Invalid JSON output: {exc}")
        continue

    actual_wf = report_data.get("selected_workflow_id")
    actual_status = report_data.get("status")
    actual_mode = report_data.get("routing_mode")

    errors = []
    if actual_wf != exp_wf:
        errors.append(f"WF mismatch: expected {exp_wf}, got {actual_wf}")
    if actual_status != exp_status:
        errors.append(f"Status mismatch: expected {exp_status}, got {actual_status}")
    if actual_exit != exp_exit:
        errors.append(f"Exit code mismatch: expected {exp_exit}, got {actual_exit}")
    if actual_mode != "offline":
        errors.append(f"Routing mode mismatch: expected 'offline', got '{actual_mode}'")

    if errors:
        failures.append((slug, "; ".join(errors)))
        print(f"[FAIL] {slug:<28} | {'; '.join(errors)}")
    else:
        passed += 1
        wf_display = actual_wf if actual_wf else "None"
        print(f"[PASS] {slug:<28} | WF={wf_display:<6} | Status={actual_status:<20} | Exit={actual_exit}")

print("\n" + "=" * 72)
print(f"Results: {passed} PASSED, {len(failures)} FAILED out of {len(expected_data)} test cases.")
print("=" * 72)

if failures:
    sys.exit(1)
sys.exit(0)
EOF

echo ""
echo "Benchmark suite execution completed successfully."
