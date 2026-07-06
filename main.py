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
    mochi.add_task(Task("Morning walk", time(7, 30), Frequency.DAILY, duration_minutes=30, priority=Priority.MEDIUM))
    mochi.add_task(Task("Meds", time(8, 0), Frequency.DAILY, duration_minutes=5, priority=Priority.HIGH))
    mochi.add_task(Task("Evening walk", time(18, 0), Frequency.DAILY, duration_minutes=20, priority=Priority.LOW))
    luna.add_task(Task("Feed", time(8, 0), Frequency.DAILY, duration_minutes=10, priority=Priority.MEDIUM))
    luna.add_task(Task("Vet visit", time(15, 0), Frequency.WEEKLY, duration_minutes=45, priority=Priority.HIGH))

    # 3. Build the schedule and print it, ordered by time across all pets.
    scheduler = Scheduler(owner)
    print(scheduler.render_schedule())


if __name__ == "__main__":
    main()
