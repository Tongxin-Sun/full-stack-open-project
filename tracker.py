import json
import datetime
import os
import time
import re

LOG_FILE = "time_log.json"
MD_FILE = "README.md"


def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def parse_duration(duration_str):
    h, m, s = map(int, duration_str.strip().split(":"))
    return datetime.timedelta(hours=h, minutes=m, seconds=s)


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    h, remainder = divmod(total_seconds, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02}:{m:02}:{s:02}"


def update_md(log):
    if not os.path.exists(MD_FILE):
        print(f"{MD_FILE} not found.")
        return

    with open(MD_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    current_part = None
    part_total_times = {}

    # First pass: calculate all subpart times and total part times
    for key, entries in log.items():
        total = sum((entry["end"] - entry["start"] for entry in entries), 0)
        h, m = divmod(int(total), 60)
        s = m % 60
        part, sub = key[:-1], key[-1] if not key[-1].isdigit() else None
        if sub:
            part_total_times.setdefault(part, {})[sub] = datetime.timedelta(
                seconds=total
            )
        else:
            part_total_times.setdefault(key, {})

    # Second pass: update README.md lines
    part_pattern = re.compile(r"^- \[ \] Part (\d+):(.+?)( \[\d{2}:\d{2}:\d{2}\])?$")
    subpart_pattern = re.compile(r"^\s+- ([a-z])\. (.+?) \[\d{2}:\d{2}:\d{2}\]$")

    for line in lines:
        part_match = part_pattern.match(line)
        subpart_match = subpart_pattern.match(line)

        if part_match:
            current_part = part_match.group(1)
            title = part_match.group(2).strip()
            total = sum(
                part_total_times.get(current_part, {}).values(), datetime.timedelta()
            )
            new_line = (
                f"- [ ] Part {current_part}: {title} [{format_timedelta(total)}]\n"
            )
            new_lines.append(new_line)
        elif subpart_match and current_part:
            sub = subpart_match.group(1)
            subtitle = subpart_match.group(2)
            duration = part_total_times.get(current_part, {}).get(
                sub, datetime.timedelta()
            )
            new_lines.append(
                f"    - {sub}. {subtitle} [{format_timedelta(duration)}]\n"
            )
        else:
            new_lines.append(line)

    with open(MD_FILE, "w") as f:
        f.writelines(new_lines)


def main():
    print("📘 Full Stack Open Time Tracker")
    log = load_log()

    part = input("👉 Which part are you working on? (e.g., 0a, 1b): ").strip().lower()
    if not re.match(r"^\d+[a-z]?$", part):
        print("❌ Invalid part or subpart format.")
        return

    print("⌛ Type 'start' to begin timing...")
    while input("> ").strip().lower() != "start":
        print("⌛ Waiting for 'start'...")

    start_time = time.time()
    print("✅ Timer started. Type 'end' when you finish.")

    while input("> ").strip().lower() != "end":
        print("⌛ Waiting for 'end'...")

    end_time = time.time()
    elapsed = end_time - start_time
    duration_str = format_timedelta(datetime.timedelta(seconds=elapsed))

    if part not in log:
        log[part] = []

    log[part].append(
        {
            "start": int(start_time),
            "end": int(end_time),
            "duration": duration_str,
            "timestamp": datetime.datetime.now().isoformat(),
        }
    )

    save_log(log)
    update_md(log)

    print(f"⏱️ Session logged: {duration_str} for Part {part}")


if __name__ == "__main__":
    main()
