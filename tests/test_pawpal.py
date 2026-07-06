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


# ---------------------------------------------------------------------------
# Sorting correctness — tasks come back in chronological order.
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() orders every task earliest-first regardless of the order
    they were added and regardless of which pet they belong to."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Deliberately added out of chronological order and interleaved by pet.
    mochi.add_task(Task("Evening walk", time(18, 0)))
    luna.add_task(Task("Breakfast", time(6, 30)))
    mochi.add_task(Task("Lunch", time(12, 0)))
    luna.add_task(Task("Midnight check", time(23, 45)))
    mochi.add_task(Task("Dawn meds", time(5, 0)))

    ordered = [t.time for t in Scheduler(owner).sort_by_time()]

    assert ordered == sorted(ordered)
    assert ordered == [time(5, 0), time(6, 30), time(12, 0), time(18, 0), time(23, 45)]


def test_sort_by_time_on_empty_owner_returns_empty_list():
    """Sorting with no pets/tasks is a no-op, not an error."""
    assert Scheduler(Owner("Jordan")).sort_by_time() == []


def test_tasks_for_pet_are_time_ordered():
    """A single pet's pending tasks come back earliest-first."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Dinner", time(19, 0)))
    pet.add_task(Task("Breakfast", time(7, 0)))

    ordered = [t.description for t in Scheduler(owner).tasks_for_pet(pet)]

    assert ordered == ["Breakfast", "Dinner"]


# ---------------------------------------------------------------------------
# Recurrence logic — completing a recurring task refills the plan.
# ---------------------------------------------------------------------------

def test_recurring_follow_up_preserves_task_attributes():
    """The auto-created next occurrence copies description, time, frequency,
    duration and priority — only the due date advances and completion resets."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    walk = Task("Walk", time(7, 30), Frequency.DAILY, duration_minutes=45,
                priority=Priority.HIGH, due_date=date(2026, 1, 1))
    pet.add_task(walk)

    follow_up = Scheduler(owner).mark_task_complete(walk)

    assert follow_up.description == "Walk"
    assert follow_up.time == time(7, 30)
    assert follow_up.frequency is Frequency.DAILY
    assert follow_up.duration_minutes == 45
    assert follow_up.priority is Priority.HIGH
    assert follow_up.completed is False


def test_completed_recurring_task_surfaces_on_its_next_day():
    """After completing today's daily task, the fresh occurrence is hidden today
    but appears in the plan for the following day."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    today = date.today()
    walk = Task("Walk", time(7, 30), Frequency.DAILY, due_date=today)
    pet.add_task(walk)
    sched = Scheduler(owner)

    sched.mark_task_complete(walk)

    # Nothing pending for today (original is done, follow-up is future-dated).
    assert sched.daily_schedule(today) == []
    # The follow-up shows up tomorrow.
    tomorrow_tasks = [t.description for _, t in sched.daily_schedule(today + timedelta(days=1))]
    assert tomorrow_tasks == ["Walk"]


def test_mark_complete_on_foreign_task_does_nothing():
    """Completing a task that belongs to no pet of this owner returns None and
    spawns no follow-up (no ownership, no side effects)."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    orphan = Task("Walk", time(7, 30), Frequency.DAILY)  # never added to a pet

    result = Scheduler(owner).mark_task_complete(orphan)

    assert result is None
    assert orphan.completed is False
    assert pet.get_tasks() == []


# ---------------------------------------------------------------------------
# Conflict detection — extra edge cases beyond the two same-time tasks.
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_three_way_overlap_in_one_warning():
    """Three tasks at the same time collapse into a single warning naming all
    three, not three separate warnings."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Meds", time(8, 0)))
    pet.add_task(Task("Feed", time(8, 0)))
    pet.add_task(Task("Walk", time(8, 0)))

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert all(name in warnings[0] for name in ("Meds", "Feed", "Walk"))


def test_detect_conflicts_reports_each_clashing_time_separately():
    """Two independent time clashes yield two warnings, time-ordered."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Meds", time(8, 0)))
    pet.add_task(Task("Feed", time(8, 0)))
    pet.add_task(Task("Walk", time(18, 0)))
    pet.add_task(Task("Play", time(18, 0)))

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 2
    assert "08:00" in warnings[0]   # earlier clash reported first
    assert "18:00" in warnings[1]


def test_detect_conflicts_ignores_completed_tasks():
    """A completed task at the same time as a pending one is not a conflict —
    only schedulable (pending, due) tasks are inspected."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    done = Task("Meds", time(8, 0))
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Feed", time(8, 0)))

    assert Scheduler(owner).detect_conflicts() == []


# ---------------------------------------------------------------------------
# Empty / boundary states — a pet with no tasks, an owner with no pets, etc.
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_has_empty_schedule():
    """An owner whose pet has no tasks produces an empty plan and no next task,
    without raising."""
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))
    sched = Scheduler(owner)

    assert sched.daily_schedule() == []
    assert sched.pending_tasks() == []
    assert sched.next_task() is None


def test_owner_with_no_pets_reports_nothing_pending():
    """With no pets at all, the rendered schedule says nothing is pending."""
    sched = Scheduler(Owner("Jordan"))

    assert sched.all_tasks() == []
    assert "nothing pending" in sched.render_schedule()


def test_next_task_returns_earliest_pending():
    """next_task() is the first entry of the ordered daily schedule."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Dinner", time(19, 0)))
    pet.add_task(Task("Breakfast", time(7, 0)))

    pet_out, task_out = Scheduler(owner).next_task()

    assert pet_out is pet
    assert task_out.description == "Breakfast"


def test_completed_tasks_excluded_from_pending_and_duration():
    """Completed tasks drop out of the pending list and stop counting toward the
    pending-duration total."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    done = Task("Walk", time(7, 0), duration_minutes=30)
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Feed", time(8, 0), duration_minutes=15))
    sched = Scheduler(owner)

    assert [t.description for t in sched.pending_tasks()] == ["Feed"]
    assert sched.total_duration() == 15  # the completed 30-min walk is not counted


def test_filter_tasks_by_pet_and_completion():
    """filter_tasks narrows by owning pet's name and by completion status;
    passing neither returns everything."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    done = Task("Walk", time(7, 0))
    done.mark_complete()
    mochi.add_task(done)
    mochi.add_task(Task("Feed", time(8, 0)))
    luna.add_task(Task("Groom", time(9, 0)))
    sched = Scheduler(owner)

    assert len(sched.filter_tasks()) == 3                     # no filter → all
    assert {t.description for t in sched.filter_tasks(pet_name="Mochi")} == {"Walk", "Feed"}
    assert [t.description for t in sched.filter_tasks(completed=True)] == ["Walk"]
    assert [t.description for t in sched.filter_tasks(completed=False, pet_name="Mochi")] == ["Feed"]


def test_end_time_clamps_at_end_of_day():
    """A task whose duration would spill past midnight is clamped to 23:59
    rather than rolling into the next day."""
    late = Task("Late night check", time(23, 50), duration_minutes=30)

    assert late.end_time() == time(23, 59)
