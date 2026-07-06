# Logic layer where all my backend classes live

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, timedelta
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


class Priority(Enum):
    """How urgent a task is. The numeric value doubles as the sort rank
    (1 = most urgent) so the Scheduler can break ties between same-time tasks
    without needing a separate lookup table."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3

    def __str__(self) -> str:
        """Return a capitalized label (e.g. 'High') for display."""
        return self.name.capitalize()


@dataclass(frozen=True)
class TimeWindow:
    """An inclusive clock-time window (e.g. 06:00–10:00) used to express when an
    owner prefers a kind of activity to happen."""
    start: time
    end: time

    def contains(self, t: time) -> bool:
        """True if `t` falls within this window (endpoints included)."""
        return self.start <= t <= self.end

    def __str__(self) -> str:
        """Return the window as 'HH:MM–HH:MM' for display."""
        return f"{self.start.strftime('%H:%M')}–{self.end.strftime('%H:%M')}"


class Preferences:
    """An owner's preferred time windows for kinds of care, keyed by an activity
    keyword that is matched case-insensitively against a task's description
    (e.g. 'walk' matches 'Morning walk' and 'Evening walk').

    A kind of activity can have several acceptable windows, so feeding in the
    morning *and* the evening is expressible."""

    def __init__(self) -> None:
        """Create an empty set of preferences."""
        self.windows: dict[str, list[TimeWindow]] = {}

    def prefer(self, activity: str, start: time, end: time) -> None:
        """Register a preferred window for any task whose description contains
        `activity`. Call repeatedly with the same activity to allow more than
        one window."""
        self.windows.setdefault(activity.lower(), []).append(TimeWindow(start, end))

    def windows_for(self, description: str) -> list[TimeWindow]:
        """Every preferred window whose activity keyword appears in `description`."""
        text = description.lower()
        matches: list[TimeWindow] = []
        for keyword, windows in self.windows.items():
            if keyword in text:
                matches.extend(windows)
        return matches

    def is_satisfied(self, task: Task) -> bool:
        """True if the task has no matching preference (nothing to violate) or its
        start time falls inside at least one preferred window."""
        windows = self.windows_for(task.description)
        return not windows or any(w.contains(task.time) for w in windows)


@dataclass
class Task:
    """A single activity for a pet: what to do, when, how often, and whether
    it's done yet."""
    description: str
    time: time
    frequency: Frequency = Frequency.DAILY
    duration_minutes: int = 15
    priority: Priority = Priority.MEDIUM
    due_date: date = field(default_factory=date.today)
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

    def next_occurrence(self) -> Task | None:
        """Build the follow-up for a recurring task: a fresh, not-yet-done copy
        due on the next date this task's frequency calls for.

        Daily tasks advance by one day and weekly tasks by seven, computed with
        timedelta so month/year rollovers stay correct. Returns None for one-off
        (ONCE) tasks, which don't repeat."""
        intervals = {
            Frequency.DAILY: timedelta(days=1),
            Frequency.WEEKLY: timedelta(weeks=1),
        }
        delta = intervals.get(self.frequency)
        if delta is None:  # Frequency.ONCE — nothing to repeat.
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_date=self.due_date + delta,
        )

    def end_time(self) -> time:
        """Return the clock time this task finishes (start + duration), clamped
        to the same day so it never rolls past 23:59."""
        total = self.time.hour * 60 + self.time.minute + self.duration_minutes
        total = min(total, 23 * 60 + 59)
        return time(total // 60, total % 60)

    def __str__(self) -> str:
        """Return a one-line summary with status, time, duration, priority, and frequency."""
        box = "✅" if self.completed else "⬜"
        return (f"{box} {self.time.strftime('%H:%M')} ({self.duration_minutes}m) "
                f"— {self.description} [{self.priority}] ({self.frequency})")


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
        """Create an owner with a name, an empty list of pets, and an empty set
        of care preferences."""
        self.name = name
        self.pets: list[Pet] = []
        self.preferences = Preferences()

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

    def total_duration(self) -> int:
        """Total minutes of care still pending across all pets."""
        return sum(t.duration_minutes for t in self.pending_tasks())

    def daily_schedule(self, on_date: date | None = None) -> list[tuple[Pet, Task]]:
        """The plan for a single day: pending (Pet, Task) pairs due on or before
        `on_date` (default today), ordered by time with priority breaking ties
        so the more urgent of two same-time tasks comes first.

        Using 'on or before' means an overdue task carries over instead of
        silently vanishing, while future-dated occurrences (e.g. tomorrow's
        auto-created recurrence) stay out until their day arrives."""
        on_date = on_date or date.today()
        pending = [(pet, task) for pet, task in self.owner.iter_pet_tasks()
                   if not task.completed and task.due_date <= on_date]
        return sorted(pending, key=lambda pair: (pair[1].time, pair[1].priority.value))

    def tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Pending tasks for one pet, ordered by time (priority breaks ties)."""
        return sorted(pet.get_pending_tasks(), key=lambda t: (t.time, t.priority.value))

    def sort_by_time(self) -> list[Task]:
        """Every task sorted by start time, earliest first.

        `task.time` is a datetime.time, which compares chronologically on its
        own, so the lambda keys straight on it — no HH:MM string parsing needed."""
        return sorted(self.all_tasks(), key=lambda task: task.time)

    def filter_tasks(self, completed: bool | None = None,
                     pet_name: str | None = None) -> list[Task]:
        """Tasks filtered by completion status and/or owning pet's name.

        Pass either or both; a None argument means 'don't filter on that field',
        so filter_tasks() with no arguments returns everything."""
        matches: list[Task] = []
        for pet, task in self.owner.iter_pet_tasks():
            if completed is not None and task.completed != completed:
                continue
            if pet_name is not None and pet.name != pet_name:
                continue
            matches.append(task)
        return matches

    def group_by_frequency(self) -> dict[Frequency, list[Task]]:
        """Bucket all tasks by how often they recur."""
        buckets: dict[Frequency, list[Task]] = {f: [] for f in Frequency}
        for task in self.all_tasks():
            buckets[task.frequency].append(task)
        return buckets

    def group_by_priority(self) -> dict[Priority, list[Task]]:
        """Bucket all tasks by urgency, most urgent first."""
        buckets: dict[Priority, list[Task]] = {p: [] for p in Priority}
        for task in self.all_tasks():
            buckets[task.priority].append(task)
        return buckets

    def next_task(self) -> tuple[Pet, Task] | None:
        """The earliest pending task, or None if everything is done."""
        schedule = self.daily_schedule()
        return schedule[0] if schedule else None

    def detect_conflicts(self, on_date: date | None = None) -> list[str]:
        """Lightweight conflict check for the day's plan: flag any tasks that
        share the same start time, whether they belong to the same pet or to
        different pets.

        Returns a list of human-readable warning strings — empty when the day is
        conflict-free — so callers can print a heads-up instead of the program
        crashing. Only the schedulable tasks from daily_schedule() are inspected,
        so completed and future-dated tasks never raise a false alarm."""
        by_time: dict[time, list[tuple[Pet, Task]]] = {}
        for pet, task in self.daily_schedule(on_date):
            by_time.setdefault(task.time, []).append((pet, task))

        warnings: list[str] = []
        for start, pairs in sorted(by_time.items()):
            if len(pairs) > 1:
                who = ", ".join(f"{task.description} ({pet.name})"
                                for pet, task in pairs)
                warnings.append(
                    f"⚠️  Conflict at {start.strftime('%H:%M')} — "
                    f"{len(pairs)} tasks overlap: {who}."
                )
        return warnings

    def preference_warnings(self, on_date: date | None = None) -> list[str]:
        """Flag scheduled tasks that fall outside the owner's preferred time
        window(s) for that kind of activity.

        Returns warning strings — empty when everything fits — so the plan can
        note a mismatch (e.g. a walk booked outside the preferred morning window)
        instead of refusing to schedule it. Tasks with no matching preference are
        never flagged."""
        prefs = self.owner.preferences
        warnings: list[str] = []
        for pet, task in self.daily_schedule(on_date):
            if not prefs.is_satisfied(task):
                allowed = ", ".join(str(w) for w in prefs.windows_for(task.description))
                warnings.append(
                    f"⚠️  {task.description} for {pet.name} is at "
                    f"{task.time.strftime('%H:%M')}, outside preferred window(s): "
                    f"{allowed}."
                )
        return warnings

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark a task done and, if it recurs (daily/weekly), add its next
        occurrence to the owning pet so the plan refills itself automatically.

        Returns the newly created follow-up Task, or None if the task is a
        one-off or doesn't belong to this owner. Finds the owning pet through
        the Owner's public accessors and adds via Pet.add_task, so the Scheduler
        still never reaches into Pet internals."""
        for pet, existing in self.owner.iter_pet_tasks():
            if existing is task:
                task.mark_complete()
                follow_up = task.next_occurrence()
                if follow_up is not None:
                    pet.add_task(follow_up)
                return follow_up
        return None

    def explain(self) -> list[str]:
        """Human-readable plan: one line per pending task, in order, naming the
        pet so the owner understands why/when each task happens."""
        lines: list[str] = []
        for pet, task in self.daily_schedule():
            lines.append(
                f"{task.time.strftime('%H:%M')}–{task.end_time().strftime('%H:%M')} "
                f"({task.duration_minutes}m) — {task.description} for "
                f"{pet.name} [{task.priority} priority] ({task.frequency})"
            )
        return lines

    def render_schedule(self, title: str = "Today's Schedule") -> str:
        """Format the day's plan as an aligned, columnar table for the terminal.

        Columns (TIME / status / PET / TASK / MIN / PRI / FREQ) size themselves to
        the widest value so everything lines up regardless of name length."""
        rows = self.daily_schedule()
        heading = f"{title} — {self.owner.name}"

        if not rows:
            rule = "─" * len(heading)
            return f"{heading}\n{rule}\n All tasks complete — nothing pending. 🎉"

        # Dynamic column widths based on the actual data.
        pet_w = max(len("PET"), *(len(pet.name) for pet, _ in rows))
        task_w = max(len("TASK"), *(len(task.description) for _, task in rows))
        min_w = max(len("MIN"), *(len(f"{task.duration_minutes}m") for _, task in rows))
        pri_w = max(len("PRI"), *(len(str(task.priority)) for _, task in rows))
        freq_w = max(len("FREQ"), *(len(str(task.frequency)) for _, task in rows))

        def line(t: str, mark: str, pet: str, task: str, mins: str, pri: str, freq: str) -> str:
            return (f" {t:<11} {mark:<1}  {pet:<{pet_w}}  {task:<{task_w}}  "
                    f"{mins:>{min_w}}  {pri:<{pri_w}}  {freq:<{freq_w}}").rstrip()

        header = line("TIME", "✓", "PET", "TASK", "MIN", "PRI", "FREQ")
        rule = "─" * len(header)

        body = [
            line(
                f"{task.time.strftime('%H:%M')}-{task.end_time().strftime('%H:%M')}",
                "✅" if task.completed else "⬜",
                pet.name,
                task.description,
                f"{task.duration_minutes}m",
                str(task.priority),
                str(task.frequency),
            )
            for pet, task in rows
        ]

        nxt = rows[0][1]
        # Sum only the rows shown (today + overdue) so the footer matches the
        # table; total_duration() counts every pending task regardless of date.
        total = sum(task.duration_minutes for _, task in rows)
        footer = (f"{len(rows)} pending · {total} min total · "
                  f"next: {nxt.description} @ {nxt.time.strftime('%H:%M')}")

        return "\n".join([heading, rule, header, rule, *body, rule, footer])
