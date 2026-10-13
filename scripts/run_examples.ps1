# run_examples.ps1 - Execute benchmark example requests offline and verify against expected.json
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoDir = Split-Path -Parent $ScriptDir
Set-Location $RepoDir

$PythonBin = if (Test-Path "$RepoDir\.venv\Scripts\python.exe") {
    "$RepoDir\.venv\Scripts\python.exe"
} else {
    "python"
}

$OutputDir = "$RepoDir\examples\output"
$ExpectedFile = "$RepoDir\examples\expected.json"

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host "========================================================================"
Write-Host " Running AI Workflow Agent Benchmark Suite (Offline Mode - PowerShell)"
Write-Host " Python: $PythonBin"
Write-Host " Target: $OutputDir"
Write-Host "========================================================================"

$runnerScript = @"
import json, subprocess, sys
from pathlib import Path

repo_dir = Path.cwd()
expected_file = repo_dir / 'examples' / 'expected.json'
output_dir = repo_dir / 'examples' / 'output'
output_dir.mkdir(parents=True, exist_ok=True)

with open(expected_file, 'r', encoding='utf-8') as f:
    expected_data = json.load(f)

failures = []
passed = 0

print(f'Loaded {len(expected_data)} benchmark test case(s)...\n')

env_clean = dict(
    PATH=subprocess.os.environ.get('PATH', ''),
    **{k: v for k, v in subprocess.os.environ.items() if 'API_KEY' not in k and k != 'LLM_PROVIDER'}
)

for slug, spec in expected_data.items():
    req = spec['request']
    exp_wf = spec['expected_workflow_id']
    exp_status = spec['expected_status']
    exp_exit = spec['expected_exit_code']

    txt_file = output_dir / f'{slug}.txt'
    json_file = output_dir / f'{slug}.json'

    p_txt = subprocess.run([sys.executable, '-m', 'app.main', req], capture_output=True, text=True, env=env_clean)
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(p_txt.stdout)

    p_json = subprocess.run([sys.executable, '-m', 'app.main', '--json', req], capture_output=True, text=True, env=env_clean)
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(p_json.stdout)

    try:
        report = json.loads(p_json.stdout)
    except Exception as exc:
        failures.append((slug, f'JSON error: {exc}'))
        print(f'[FAIL] {slug:<28} | Invalid JSON: {exc}')
        continue

    actual_wf = report.get('selected_workflow_id')
    actual_status = report.get('status')
    actual_exit = p_json.returncode
    actual_mode = report.get('routing_mode')

    errs = []
    if actual_wf != exp_wf: errs.append(f'WF mismatch ({exp_wf} != {actual_wf})')
    if actual_status != exp_status: errs.append(f'Status mismatch ({exp_status} != {actual_status})')
    if actual_exit != exp_exit: errs.append(f'Exit mismatch ({exp_exit} != {actual_exit})')
    if actual_mode != 'offline': errs.append(f'Mode mismatch ({actual_mode})')

    if errs:
        failures.append((slug, '; '.join(errs)))
        print(f'[FAIL] {slug:<28} | {\"; \".join(errs)}')
    else:
        passed += 1
        wf_disp = actual_wf if actual_wf else 'None'
        print(f'[PASS] {slug:<28} | WF={wf_disp:<6} | Status={actual_status:<20} | Exit={actual_exit}')

print('\n' + '=' * 72)
print(f'Results: {passed} PASSED, {len(failures)} FAILED out of {len(expected_data)} test cases.')
print('=' * 72)

if failures: sys.exit(1)
sys.exit(0)
"@

& $PythonBin -c $runnerScript
if ($LASTEXITCODE -ne 0) {
    exit 1
}
