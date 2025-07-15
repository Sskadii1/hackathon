from parse_report import parse_report
from update_catalog import search_kb_download_link
from patch_runner import download_patch, run_patch
from logger import log
from summary_writer import add_summary, write_summary
import time
import json

config = json.load(open("config.json"))
batch_id = config.get("batch_id", "test-batch")
records = parse_report(config["input_file"])

for row in records:
    cve = row["CVEID"]
    kbid = row["KBID"]

    log("INFO", f"Processing {cve} ({kbid})")

    # tìm link download
    link = search_kb_download_link(kbid)
    if not link:
        log("ERROR", f"No download found for {kbid}")
        add_summary(cve, kbid, "Failed", "Patch not found in Microsoft Catalog")
        continue

    # tải file
    patch_file = download_patch(kbid, link)
    if not patch_file:
        add_summary(cve, kbid, "Failed", "Patch download error")
        continue

    # thực thi
    success = run_patch(patch_file, kbid)
    if success:
        add_summary(cve, kbid, "Success", "")
    else:
        add_summary(cve, kbid, "Failed", "Patch execution error")

# Ghi tổng kết
write_summary(batch_id)
log("INFO", f"Done. Summary written to output/summary_{batch_id}.json")
