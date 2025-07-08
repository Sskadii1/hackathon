import pandas as pd
import sys

def filter_vulns(file_path):
    df = pd.read_csv(file_path)
    df = df[df['Plugin Output'].str.contains("CVE", na=False)]
    df = df[df['Operating System'].str.contains("Windows", case=False, na=False)]
    df.to_csv("filtered_windows_vuln.csv", index=False)

if __name__ == "__main__":
    file = sys.argv[1] if len(sys.argv) > 1 else "nessus_report.csv"
    filter_vulns(file)
