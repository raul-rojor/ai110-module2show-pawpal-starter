"""Simple tests for the PawPal+ logic layer.

Run from the project root with:  pytest
"""

import os
import sys
from datetime import time

# Make pawpal_system.py (in the project root) importable from this subfolder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Task, Pet


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
