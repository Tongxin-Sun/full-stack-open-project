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
    part_line_pattern = re.compile(
        r"^- \[ \] Part (\d+):(.+?)( \[\d{2}:\d{2}:\d{2}\])?$"
    )

    for line in lines:
        match = part_line_pattern.match(line)
        if match:
            part_number = match.group(1)
            part_title = match.group(2).strip()

            total = sum(
                (
                    datetime.timedelta(seconds=(entry["end"] - entry["start"]))
                    for entry in log.get(part_number, [])
                ),
                datetime.timedelta(0),
            )
            time_str = format_timedelta(total)

            # Rebuild the line with the updated time
            new_line = f"- [ ] Part {part_number}: {part_title} [{time_str}]\n"
            new_lines.append(new_line)
        else:
            new_lines.append(line)  # Leave lines unchanged if they don't match

    with open(MD_FILE, "w") as f:
        f.writelines(new_lines)


def main():
    print("📘 Full Stack Open Time Tracker")
    log = load_log()

    part = input("👉 Which part are you working on? (e.g., 0 for Part 0): ").strip()
    if not part.isdigit():
        print("❌ Invalid part number.")
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

    # Save to log
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
