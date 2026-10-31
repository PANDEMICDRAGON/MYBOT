import os, json, subprocess, datetime, pathlib

def run_audit(target_dir: str = '.'):
    results = []
    # Check for known vulnerable packages (pip freeze)
    try:
        pip_freeze = subprocess.check_output(['pip', 'freeze'], text=True)
        for line in pip_freeze.splitlines():
            pkg = line.split('==')[0]
            # simplistic CVE check placeholder
            if pkg.lower() in {'django', 'flask', 'requests'}:
                results.append({
                    'package': pkg,
                    'status': 'potentially vulnerable (review required)'
                })
    except Exception as e:
        results.append({'error': f'pip freeze failed: {e}'})
    # File integrity check: look for suspicious files
    suspicious = []
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if f.endswith(('.sh', '.py', '.js')):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', errors='ignore') as fh:
                        content = fh.read()
                    if 'password' in content.lower() or 'secret' in content.lower():
                        suspicious.append(path)
                except Exception:
                    continue
    results.append({'suspicious_files': suspicious})
    # Log
    report_path = pathlib.Path('security_audit_report_')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    report_file = report_path.with_name(report_path.name + timestamp + '.json')
    with open(report_file, 'w') as out:
        json.dump(results, out, indent=2)
    return str(report_file)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run quick security audit')
    parser.add_argument('--path', default='.', help='Directory to scan')
    args = parser.parse_args()
    report = run_audit(args.path)
    print(f'Security audit completed. Report saved to {report}')
