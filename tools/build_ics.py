#!/usr/bin/env python3
"""Build calendar files from events.json.

Writes into ics/:
  YYYY-MM-all.ics, YYYY-MM-birthdays.ics   one-time imports per month
  all.ics, birthdays.ics                   full feeds for subscribing

Each event is all-day with an alert at alertTime (default 08:00) the day of.
Run from the repo root:  python3 tools/build_ics.py
"""
import json, hashlib, os, re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "events.json"), encoding="utf-8"))
name = data.get("calendarName", "Family Calendar")
hh, mm = (int(x) for x in data.get("alertTime", "08:00").split(":"))
trigger = f"PT{hh}H{mm}M" if mm else f"PT{hh}H"
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def fold(line):
    # RFC 5545: lines over 75 octets get folded
    out, b = [], line.encode("utf-8")
    while len(b) > 75:
        cut = 75
        while (b[cut] & 0xC0) == 0x80:  # don't split a UTF-8 character
            cut -= 1
        out.append(b[:cut].decode("utf-8"))
        b = b" " + b[cut:]
    out.append(b.decode("utf-8"))
    return "\r\n".join(out)

def vevent(e):
    d = date.fromisoformat(e["date"])
    uid = hashlib.sha1(f'{e["date"]}|{e["title"]}'.encode()).hexdigest()[:16]
    title = esc(e["title"])
    return [
        "BEGIN:VEVENT",
        f"UID:{uid}@familycal",
        f"DTSTAMP:{stamp}",
        f"DTSTART;VALUE=DATE:{d:%Y%m%d}",
        f"DTEND;VALUE=DATE:{d + timedelta(days=1):%Y%m%d}",
        f"SUMMARY:{title}",
        f"CATEGORIES:{e.get('type', 'other').upper()}",
        "TRANSP:TRANSPARENT",
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        f"DESCRIPTION:{title}",
        f"TRIGGER:{trigger}",
        "END:VALARM",
        "END:VEVENT",
    ]

def write(path, events, cal_name):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Family Calendar//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{esc(cal_name)}",
             "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D"]
    for e in sorted(events, key=lambda e: (e["date"], e["title"])):
        lines += vevent(e)
    lines.append("END:VCALENDAR")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(fold(l) for l in lines) + "\r\n")

events = data["events"]
bad = [e for e in events if "?" in e["title"]]
if bad:
    print("WARNING: unconfirmed titles:", [e["title"] for e in bad])

outdir = os.path.join(ROOT, "ics")
os.makedirs(outdir, exist_ok=True)
for f in os.listdir(outdir):
    if re.fullmatch(r"\d{4}-\d{2}-(all|birthdays)\.ics", f):
        os.remove(os.path.join(outdir, f))

by_month = defaultdict(list)
for e in events:
    by_month[e["date"][:7]].append(e)
for m, evs in by_month.items():
    write(os.path.join(outdir, f"{m}-all.ics"), evs, name)
    write(os.path.join(outdir, f"{m}-birthdays.ics"),
          [e for e in evs if e["type"] == "birthday"], f"{name} Birthdays")
write(os.path.join(outdir, "all.ics"), events, name)
write(os.path.join(outdir, "birthdays.ics"),
      [e for e in events if e["type"] == "birthday"], f"{name} Birthdays")
print("Built", len(events), "events across", len(by_month), "month(s)")
