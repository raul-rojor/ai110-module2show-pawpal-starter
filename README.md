# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Running `python3 main.py` adds tasks out of order (with two deliberate time
clashes), completes a recurring task (which auto-creates its next occurrence),
then demonstrates sorting, filtering, conflict detection, and preference checks
before printing the day's plan. The owner prefers walks 06:00–10:00 and feeding
06:00–09:00. The two dates are shown as placeholders here because they're computed
from the current date at runtime:

```
Completed 'Morning walk' (due <today>). Next occurrence auto-scheduled for <today + 1 day>.

All tasks sorted by time:
  ✅ 07:30 (30m) — Morning walk [Medium] (daily)
  ⬜ 07:30 (30m) — Morning walk [Medium] (daily)
  ⬜ 08:00 (5m) — Meds [High] (daily)
  ⬜ 08:00 (10m) — Feed [Medium] (daily)
  ⬜ 15:00 (45m) — Vet visit [High] (weekly)
  ⬜ 18:00 (20m) — Evening walk [Low] (daily)
  ⬜ 18:00 (15m) — Playtime [Medium] (daily)

Luna's tasks only:
  ⬜ 08:00 (10m) — Feed [Medium] (daily)
  ⬜ 15:00 (45m) — Vet visit [High] (weekly)

Still-pending tasks:
  ⬜ 08:00 (5m) — Meds [High] (daily)
  ⬜ 18:00 (20m) — Evening walk [Low] (daily)
  ⬜ 18:00 (15m) — Playtime [Medium] (daily)
  ⬜ 07:30 (30m) — Morning walk [Medium] (daily)
  ⬜ 08:00 (10m) — Feed [Medium] (daily)
  ⬜ 15:00 (45m) — Vet visit [High] (weekly)

Today's Schedule — Jordan
──────────────────────────────────────────────────────
 TIME        ✓  PET    TASK          MIN  PRI     FREQ
──────────────────────────────────────────────────────
 08:00-08:05 ⬜  Mochi  Meds           5m  High    daily
 08:00-08:10 ⬜  Luna   Feed          10m  Medium  daily
 15:00-15:45 ⬜  Luna   Vet visit     45m  High    weekly
 18:00-18:15 ⬜  Mochi  Playtime      15m  Medium  daily
 18:00-18:20 ⬜  Mochi  Evening walk  20m  Low     daily
──────────────────────────────────────────────────────
5 pending · 95 min total · next: Meds @ 08:00

Schedule warnings:
  ⚠️  Conflict at 08:00 — 2 tasks overlap: Meds (Mochi), Feed (Luna).
  ⚠️  Conflict at 18:00 — 2 tasks overlap: Playtime (Mochi), Evening walk (Mochi).

Preference warnings:
  ⚠️  Evening walk for Mochi is at 18:00, outside preferred window(s): 06:00–10:00.
```

## 🧪 Testing PawPal+

'''bash
.venv/bin/python -m pytest tests/test_pawpal.py
'''

Sample test output:

```
================================================================ test session starts ================================================================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/rrn/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 28 items                                                                                                                                  

tests/test_pawpal.py ............................                                                                                             [100%]

================================================================ 28 passed in 0.02s =================================================================
```
```Confidence level from tests:
5/5
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting | `Scheduler.sort_by_time`, `Scheduler.daily_schedule` | Ordered by start time; priority breaks ties between same-time tasks |
| Filtering | `Scheduler.filter_tasks`, `Scheduler.pending_tasks` | By completion status and/or pet name; schedule also drops future-dated tasks |
| Conflict detection | `Scheduler.detect_conflicts` | Flags tasks (same or different pet) sharing a start time; returns warnings instead of crashing |
| Owner preferences | `Preferences`, `Scheduler.preference_warnings` | Preferred windows per activity keyword (e.g. walks in the morning); flags tasks scheduled outside them |
| Recurring tasks | `Task.next_occurrence`, `Scheduler.mark_task_complete` | Completing a daily/weekly task auto-creates the next occurrence (+1 day / +7 days via `timedelta`) |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
