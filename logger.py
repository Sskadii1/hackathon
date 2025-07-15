from datetime import datetime

log_file = "patch.log"

def log(level, message):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"[{ts}] [{level}] {message}"
    print(entry)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
