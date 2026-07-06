"""Simple tests for the PawPal+ logic layer.

Run from the project root with:  pytest
"""

import os
import sys
from datetime import date, time, timedelta

# Make pawpal_system.py (in the project root) importable from this subfolder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Task, Pet, Owner, Scheduler, Priority, Frequency, TimeWindow


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip a task from not-done to done."""
    task = Task("Morning walk", time(7, 30))

    assert task.completed is False  # tasks start incomplete

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should grow that pet's task list by one."""
    pet = Pet("Mochi", "dog")

    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feed", time(8, 0)))

    assert len(pet.get_tasks()) == 1


def test_priority_breaks_ties_between_same_time_tasks():
    """When two tasks share a start time, the higher-priority one is scheduled
    first."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)

    # Same time, different priority. Added low-priority first to prove the
    # scheduler reorders by priority rather than insertion order.
    pet.add_task(Task("Feed", time(8, 0), priority=Priority.MEDIUM))
    pet.add_task(Task("Meds", time(8, 0), priority=Priority.HIGH))

    schedule = Scheduler(owner).daily_schedule()
    ordered = [task.description for _, task in schedule]

    assert ordered == ["Meds", "Feed"]


def test_task_defaults_to_medium_priority():
    """A task created without an explicit priority should default to MEDIUM."""
    task = Task("Feed", time(8, 0))

    assert task.priority is Priority.MEDIUM


def test_completing_daily_task_spawns_next_day_occurrence():
    """Completing a daily task marks it done and adds a fresh copy due one day
    later to the same pet."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    walk = Task("Walk", time(7, 30), Frequency.DAILY, due_date=date(2026, 1, 1))
    pet.add_task(walk)

    follow_up = Scheduler(owner).mark_task_complete(walk)

    assert walk.completed is True
    assert follow_up is not None
    assert follow_up.completed is False
    assert follow_up.due_date == date(2026, 1, 2)  # today + 1 day
    assert follow_up in pet.get_tasks()


def test_completing_weekly_task_spawns_occurrence_seven_days_later():
    """A weekly task's next occurrence should land seven days out."""
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat")
    owner.add_pet(pet)
    vet = Task("Vet visit", time(15, 0), Frequency.WEEKLY, due_date=date(2026, 1, 1))
    pet.add_task(vet)

    follow_up = Scheduler(owner).mark_task_complete(vet)

    assert follow_up is not None
    assert follow_up.due_date == date(2026, 1, 8)


def test_completing_once_task_does_not_recur():
    """A one-off task is completed but spawns nothing."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    groom = Task("Grooming", time(9, 0), Frequency.ONCE)
    pet.add_task(groom)

    follow_up = Scheduler(owner).mark_task_complete(groom)

    assert groom.completed is True
    assert follow_up is None
    assert len(pet.get_tasks()) == 1


def test_detect_conflicts_flags_same_time_tasks():
    """Two tasks sharing a start time — even across different pets — produce a
    warning string rather than raising."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Meds", time(8, 0)))
    luna.add_task(Task("Feed", time(8, 0)))

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Meds" in warnings[0] and "Feed" in warnings[0]


def test_detect_conflicts_returns_empty_when_no_overlap():
    """Tasks at distinct times produce no warnings."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", time(7, 30)))
    pet.add_task(Task("Feed", time(8, 0)))

    assert Scheduler(owner).detect_conflicts() == []


def test_timewindow_contains_is_inclusive():
    """A window includes its endpoints and excludes times outside it."""
    window = TimeWindow(time(6, 0), time(10, 0))

    assert window.contains(time(6, 0)) is True
    assert window.contains(time(8, 30)) is True
    assert window.contains(time(10, 0)) is True
    assert window.contains(time(10, 1)) is False


def test_preference_warning_for_task_outside_window():
    """A walk booked outside the owner's preferred morning window is flagged."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    owner.preferences.prefer("walk", time(6, 0), time(10, 0))
    pet.add_task(Task("Evening walk", time(18, 0)))

    warnings = Scheduler(owner).preference_warnings()

    assert len(warnings) == 1
    assert "Evening walk" in warnings[0]
    assert "06:00–10:00" in warnings[0]


def test_no_preference_warning_when_task_inside_any_window():
    """Feeding has two preferred windows; a task inside either raises no warning,
    and a task with no matching preference is never flagged."""
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat")
    owner.add_pet(pet)
    owner.preferences.prefer("feed", time(6, 0), time(9, 0))
    owner.preferences.prefer("feed", time(17, 0), time(19, 0))
    pet.add_task(Task("Feed", time(18, 0)))       # inside the evening window
    pet.add_task(Task("Vet visit", time(15, 0)))  # no preference for "vet"

    assert Scheduler(owner).preference_warnings() == []


def test_daily_schedule_excludes_future_dated_tasks():
    """The day's plan shows today's (and overdue) tasks but hides ones due on a
    later date, such as an auto-created next occurrence."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    overdue = Task("Overdue walk", time(7, 0), due_date=date.today() - timedelta(days=1))
    today = Task("Walk", time(7, 30), due_date=date.today())
    tomorrow = Task("Walk", time(7, 30), due_date=date.today() + timedelta(days=1))
    for t in (overdue, today, tomorrow):
        pet.add_task(t)

    scheduled = [task for _, task in Scheduler(owner).daily_schedule()]

    assert overdue in scheduled  # carries over
    assert today in scheduled
    assert tomorrow not in scheduled  # future occurrence stays hidden
