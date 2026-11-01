# Family Calendar

A free GitHub Pages site where friends add the family wall calendar's events to their phones, each with an 8 AM alert on the day.

## One-time setup (about 10 minutes)

1. Repo: https://github.com/Mewniverse/FamilyCal (private for now). Free Pages needs it **Public**, so switch it in Settings > General > Danger Zone when ready.
2. On the new repo page, click **uploading an existing file**. Drag in everything from this zip, including the `ics` and `tools` folders and the `.nojekyll` file, then click **Commit changes**.
   - Mac hides `.nojekyll`. Press Cmd+Shift+. in Finder to show it. It isn't critical if it gets left out.
3. Go to **Settings > Pages**. Under "Build and deployment," set Source to **Deploy from a branch**, Branch to **main**, folder **/ (root)**, then **Save**.
4. Wait a minute or two. Your link will be `https://mewniverse.github.io/FamilyCal/`. Send that to friends.

Note: anyone with the link can see the event names and dates, and the repo is public.

## Each month

1. Send Claude a clear photo of the month's grid (closer shots of the date squares read better).
2. Claude gives you an updated `events.json` plus the rebuilt files in `ics/`.
3. Upload them to the repo, replacing the old ones. The site updates in about 10 minutes.

Months that are over hide themselves automatically.

## Files

- `index.html` is the page friends see.
- `events.json` is the list of events, the only thing that really changes.
- `ics/` holds the calendar files built from `events.json`: per-month imports (`2026-11-all.ics`, `2026-11-birthdays.ics`) and full subscription feeds (`all.ics`, `birthdays.ics`).
- `tools/build_ics.py` rebuilds `ics/` from `events.json` (`python3 tools/build_ics.py`). Claude runs this for you.

## Known limits

- Google Calendar on Android usually ignores the 8 AM alert and uses its own default reminder.
- Subscribed calendars on iPhone drop alerts unless "Remove Alerts" is switched off when subscribing.
- Re-importing the same month adds duplicates, so each friend should import a month once.
