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

Running `python3 main.py` adds tasks out of order, completes a recurring task
(which auto-creates its next occurrence), then demonstrates sorting and filtering
before printing the day's plan. The two dates are shown as placeholders here
because they're computed from the current date at runtime:

```
Completed 'Morning walk' (due <today>). Next occurrence auto-scheduled for <today + 1 day>.

All tasks sorted by time:
  ✅ 07:30 (30m) — Morning walk [Medium] (daily)
  ⬜ 07:30 (30m) — Morning walk [Medium] (daily)
  ⬜ 08:00 (5m) — Meds [High] (daily)
  ⬜ 08:00 (10m) — Feed [Medium] (daily)
  ⬜ 15:00 (45m) — Vet visit [High] (weekly)
  ⬜ 18:00 (20m) — Evening walk [Low] (daily)

Luna's tasks only:
  ⬜ 08:00 (10m) — Feed [Medium] (daily)
  ⬜ 15:00 (45m) — Vet visit [High] (weekly)

Still-pending tasks:
  ⬜ 08:00 (5m) — Meds [High] (daily)
  ⬜ 18:00 (20m) — Evening walk [Low] (daily)
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
 18:00-18:20 ⬜  Mochi  Evening walk  20m  Low     daily
──────────────────────────────────────────────────────
4 pending · 80 min total · next: Meds @ 08:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
