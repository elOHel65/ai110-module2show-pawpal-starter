"""Tests for PawPal+ task management and basic scheduling."""

from datetime import date, datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete():
    """Completing a task changes its completion flag."""
    task = Task("Walk", 20, "high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task():
    """Adding a task increases the count and stores the same object."""
    pet = Pet("Biscuit", "dog")
    task = Task("Walk", 20, "high")
    previous_count = len(pet.tasks)
    pet.add_task(task)
    assert len(pet.tasks) == previous_count + 1
    assert pet.tasks[-1] is task


def test_collect_tasks_from_multiple_pets():
    """The owner collects all pets' tasks."""
    owner = Owner("Jordan", 60)
    for name in ("Biscuit", "Mochi"):
        pet = Pet(name, "pet")
        owner.add_pet(pet)
        pet.add_task(Task(name, 10, "high"))
    assert owner.get_all_tasks() == [pet.tasks[0] for pet in owner.pets]


def test_priority_and_time_order():
    """Priority precedes time and unscheduled tasks follow timed ties."""
    low = Task("Low", 5, "low", datetime(2026, 10, 11, 7))
    medium = Task("Medium", 5, "medium")
    late = Task("Late", 5, "high", datetime(2026, 10, 11, 10))
    early = Task("Early", 5, "high", datetime(2026, 10, 11, 8))
    untimed = Task("Untimed", 5, "high")
    tasks = [low, medium, late, untimed, early]
    assert Scheduler(Owner("Jordan", 60)).sort_tasks(tasks) == [early, late, untimed, medium, low]


def test_daily_filter_and_budget():
    """Filter completed and other-date one-offs and skip oversized tasks."""
    owner = Owner("Jordan", 20)
    pet = Pet("Mochi", "cat")
    owner.add_pet(pet)
    large = Task("Large", 30, "high")
    done = Task("Done", 5, "high", completed=True)
    other_day = Task("Other day", 5, "high", datetime(2026, 10, 10, 8))
    recurring = Task("Recurring", 5, "medium", datetime(2026, 10, 10, 9), "daily")
    small = Task("Small", 15, "low", datetime(2026, 10, 11, 10))
    for task in (large, done, other_day, recurring, small):
        pet.add_task(task)
    assert Scheduler(owner).generate_daily_plan(date(2026, 10, 11)) == [recurring, small]
    assert recurring.scheduled_time == datetime(2026, 10, 10, 9)


def test_conflicts_and_touching_boundaries():
    """Detect overlaps but allow consecutive tasks and ignore untimed tasks."""
    first = Task("First", 30, "high", datetime(2026, 10, 11, 8))
    overlapping = Task("Overlap", 10, "high", datetime(2026, 10, 11, 8, 10))
    adjacent = Task("Adjacent", 10, "high", datetime(2026, 10, 11, 8, 30))
    untimed = Task("Untimed", 10, "high")
    assert Scheduler(Owner("Jordan", 60)).detect_conflicts([first, overlapping, adjacent, untimed]) == [(first, overlapping)]
