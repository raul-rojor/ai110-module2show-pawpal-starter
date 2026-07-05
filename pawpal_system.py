# Logic layer where all my backend classes live

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from enum import Enum


class Frequency(Enum):
    """How often a task recurs. Kept as an enum so the Scheduler can filter/group
    on it without matching against free-form strings."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"

    def __str__(self) -> str:
        """Return the lowercase label (e.g. 'daily') for display."""
        return self.value


@dataclass
class Task:
    """A single activity for a pet: what to do, when, how often, and whether
    it's done yet."""
    description: str
    time: time
    frequency: Frequency = Frequency.DAILY
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        self.completed = False

    def toggle(self) -> None:
        """Flip the completion status between done and not done."""
        self.completed = not self.completed

    def __str__(self) -> str:
        """Return a one-line summary with a status box, time, and frequency."""
        box = "✅" if self.completed else "⬜"
        return f"{box} {self.time.strftime('%H:%M')} — {self.description} ({self.frequency})"


class Pet:
    """Stores a pet's details and owns the list of tasks for that pet."""

    def __init__(self, name: str, species: str) -> None:
        """Create a pet with a name, species, and an empty task list."""
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's list if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return list(self.tasks)

    def get_pending_tasks(self) -> list[Task]:
        """Return only the tasks that aren't completed yet."""
        return [t for t in self.tasks if not t.completed]

    def __str__(self) -> str:
        """Return a one-line summary of the pet and its task count."""
        return f"{self.name} ({self.species}) — {len(self.tasks)} task(s)"


class Owner:
    """Manages multiple pets and provides access to all of their tasks.

    The Owner is the single source of truth for pet data. Anything that needs
    tasks (like the Scheduler) goes through these public accessors instead of
    reaching into each Pet's internals."""

    def __init__(self, name: str) -> None:
        """Create an owner with a name and an empty list of pets."""
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Flatten every pet's tasks into one list."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def iter_pet_tasks(self) -> list[tuple[Pet, Task]]:
        """Every task paired with the pet it belongs to. This keeps the
        pet↔task link intact for callers (e.g. the Scheduler) that need to know
        *whose* task each one is."""
        pairs: list[tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.get_tasks():
                pairs.append((pet, task))
        return pairs

    def __str__(self) -> str:
        """Return a one-line summary of the owner and pet count."""
        return f"Owner {self.name} with {len(self.pets)} pet(s)"


class Scheduler:
    """The 'brain': retrieves, organizes, and manages tasks across all of an
    owner's pets.

    The Scheduler never touches Pet.tasks directly — it asks the Owner for data
    through the Owner's public methods (get_all_tasks / iter_pet_tasks). That
    keeps the Scheduler decoupled from how pets store their tasks."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler bound to one owner as its data source."""
        self.owner = owner

    def all_tasks(self) -> list[Task]:
        """Every task across every pet, via the Owner."""
        return self.owner.get_all_tasks()

    def pending_tasks(self) -> list[Task]:
        """Only the tasks still to be done."""
        return [t for t in self.all_tasks() if not t.completed]

    def daily_schedule(self) -> list[tuple[Pet, Task]]:
        """The plan for the day: every pending (Pet, Task) pair ordered by time
        so the owner sees what to do and in what order."""
        pending = [(pet, task) for pet, task in self.owner.iter_pet_tasks()
                   if not task.completed]
        return sorted(pending, key=lambda pair: pair[1].time)

    def tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Pending tasks for one pet, ordered by time."""
        return sorted(pet.get_pending_tasks(), key=lambda t: t.time)

    def group_by_frequency(self) -> dict[Frequency, list[Task]]:
        """Bucket all tasks by how often they recur."""
        buckets: dict[Frequency, list[Task]] = {f: [] for f in Frequency}
        for task in self.all_tasks():
            buckets[task.frequency].append(task)
        return buckets

    def next_task(self) -> tuple[Pet, Task] | None:
        """The earliest pending task, or None if everything is done."""
        schedule = self.daily_schedule()
        return schedule[0] if schedule else None

    def explain(self) -> list[str]:
        """Human-readable plan: one line per pending task, in order, naming the
        pet so the owner understands why/when each task happens."""
        lines: list[str] = []
        for pet, task in self.daily_schedule():
            lines.append(
                f"{task.time.strftime('%H:%M')} — {task.description} for "
                f"{pet.name} ({task.frequency})"
            )
        return lines

    def render_schedule(self, title: str = "Today's Schedule") -> str:
        """Format the day's plan as an aligned, columnar table for the terminal.

        Columns (TIME / status / PET / TASK / FREQ) size themselves to the
        widest value so everything lines up regardless of name length."""
        rows = self.daily_schedule()
        heading = f"{title} — {self.owner.name}"

        if not rows:
            rule = "─" * len(heading)
            return f"{heading}\n{rule}\n All tasks complete — nothing pending. 🎉"

        # Dynamic column widths based on the actual data.
        pet_w = max(len("PET"), *(len(pet.name) for pet, _ in rows))
        task_w = max(len("TASK"), *(len(task.description) for _, task in rows))
        freq_w = max(len("FREQ"), *(len(str(task.frequency)) for _, task in rows))

        def line(t: str, mark: str, pet: str, task: str, freq: str) -> str:
            return (f" {t:<6} {mark:<1}  {pet:<{pet_w}}  "
                    f"{task:<{task_w}}  {freq:<{freq_w}}").rstrip()

        header = line("TIME", "✓", "PET", "TASK", "FREQ")
        rule = "─" * len(header)

        body = [
            line(
                task.time.strftime("%H:%M"),
                "✅" if task.completed else "⬜",
                pet.name,
                task.description,
                str(task.frequency),
            )
            for pet, task in rows
        ]

        nxt = rows[0][1]
        footer = (f"{len(rows)} pending · next: {nxt.description} "
                  f"@ {nxt.time.strftime('%H:%M')}")

        return "\n".join([heading, rule, header, rule, *body, rule, footer])
