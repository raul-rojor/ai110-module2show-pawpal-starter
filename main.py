"""Temporary testing ground: verify the PawPal+ logic works in the terminal.

Run with:  python3 main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler, Frequency


def main() -> None:
    # 1. Create an owner and two pets.
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # 2. Add tasks with different times to the pets.
    mochi.add_task(Task("Morning walk", time(7, 30), Frequency.DAILY))
    mochi.add_task(Task("Evening walk", time(18, 0), Frequency.DAILY))
    luna.add_task(Task("Feed", time(8, 0), Frequency.DAILY))
    luna.add_task(Task("Vet visit", time(15, 0), Frequency.WEEKLY))

    # 3. Build the schedule and print it, ordered by time across all pets.
    scheduler = Scheduler(owner)
    print(scheduler.render_schedule())


if __name__ == "__main__":
    main()
