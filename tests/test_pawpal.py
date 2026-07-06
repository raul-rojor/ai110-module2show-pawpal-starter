"""Simple tests for the PawPal+ logic layer.

Run from the project root with:  pytest
"""

import os
import sys
from datetime import time

# Make pawpal_system.py (in the project root) importable from this subfolder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Task, Pet, Owner, Scheduler, Priority


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
