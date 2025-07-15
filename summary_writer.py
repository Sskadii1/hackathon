import json
import os

summary_data = []

def add_summary(cveid, kbid, status, reason):
    summary_data.append({
        "CVEID": cveid,
        "KBID": kbid,
        "Status": status,
        "Reason": reason
    })

def write_summary(batch_id):
    os.makedirs("output", exist_ok=True)
    with open(f"output/summary_{batch_id}.json", "w") as f:
        json.dump(summary_data, f, indent=2)
