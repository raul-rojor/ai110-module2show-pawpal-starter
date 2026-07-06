"""Temporary testing ground: verify the PawPal+ logic works in the terminal.

Run with:  python3 main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler, Frequency, Priority


def main() -> None:
    # 1. Create an owner and two pets.
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # 2. Add tasks with different times and priorities to the pets.
    #    Note the two 08:00 tasks: priority breaks the tie so Meds (HIGH)
    #    lands before Feed (MEDIUM).
    morning_walk = Task("Morning walk", time(7, 30), Frequency.DAILY, duration_minutes=30, priority=Priority.MEDIUM)
    mochi.add_task(morning_walk)
    mochi.add_task(Task("Meds", time(8, 0), Frequency.DAILY, duration_minutes=5, priority=Priority.HIGH))
    mochi.add_task(Task("Evening walk", time(18, 0), Frequency.DAILY, duration_minutes=20, priority=Priority.LOW))
    luna.add_task(Task("Feed", time(8, 0), Frequency.DAILY, duration_minutes=10, priority=Priority.MEDIUM))
    luna.add_task(Task("Vet visit", time(15, 0), Frequency.WEEKLY, duration_minutes=45, priority=Priority.HIGH))

    scheduler = Scheduler(owner)

    # 3. Completing a recurring task auto-creates its next occurrence: the
    #    original is marked done and a fresh copy is added for the next day.
    follow_up = scheduler.mark_task_complete(morning_walk)
    print(
        f"Completed '{morning_walk.description}' (due {morning_walk.due_date}). "
        f"Next occurrence auto-scheduled for {follow_up.due_date}.\n"
    )

    # 4. Sorting: tasks come back in time order even though they were added
    #    out of order above (18:00 before 08:00, etc.).
    print("All tasks sorted by time:")
    for task in scheduler.sort_by_time():
        print(f"  {task}")

    # 5. Filtering: by pet name, then by completion status.
    print("\nLuna's tasks only:")
    for task in scheduler.filter_tasks(pet_name="Luna"):
        print(f"  {task}")

    print("\nStill-pending tasks:")
    for task in scheduler.filter_tasks(completed=False):
        print(f"  {task}")

    # 6. The full time-ordered plan for good measure.
    print()
    print(scheduler.render_schedule())


if __name__ == "__main__":
    main()
