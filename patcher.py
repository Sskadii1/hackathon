import pandas as pd
import subprocess
import re

def get_available_updates():
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-WindowsUpdate -MicrosoftUpdate | Out-String'],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return ""

def extract_kb_ids(update_output):
    kb_ids = re.findall(r'KB\d{7}', update_output)
    return list(set(kb_ids))

def check_cve_in_updates(cve_list, update_output):
    found_cves = {}
    for cve in cve_list:
        if cve in update_output:
            matches = re.findall(r'KB\d{7}', update_output)
            found_cves[cve] = matches
    return found_cves

def install_updates(kb_ids):
    for kb in kb_ids:
        cmd = [
            'powershell', '-Command',
            f'Install-WindowsUpdate -KBArticleID {kb} -AcceptAll -AutoReboot'
        ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            pass

def main():
    df = pd.read_csv('filtered_windows_vuln.csv')
    cve_column = next((col for col in df.columns if "CVE" in col), None)
    if not cve_column:
        return

    cve_list = df[cve_column].dropna().unique()

    update_output = get_available_updates()
    kb_ids_available = extract_kb_ids(update_output)
    found_cves = check_cve_in_updates(cve_list, update_output)

    if found_cves:
        kbs_to_install = set(kb for kbs in found_cves.values() for kb in kbs if kb in kb_ids_available)
        install_updates(kbs_to_install)

if __name__ == "__main__":
    main()
