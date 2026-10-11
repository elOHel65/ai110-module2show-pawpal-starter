"""Tests for PawPal+ task management and basic scheduling."""

from datetime import date, datetime, timedelta

import pytest

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


def test_sort_by_time_preserves_input_and_equal_time_order():
    """Time sorting is stable, ignores priority, and places unscheduled last."""
    scheduler = Scheduler(Owner("Jordan", 60))
    untimed = Task("Untimed", 5, "high")
    late = Task("Late", 5, "high", datetime(2026, 10, 11, 10))
    early = Task("Early", 5, "low", datetime(2026, 10, 11, 8))
    tie = Task("Tie", 5, "medium", early.scheduled_time)
    tasks = [untimed, late, early, tie]
    assert scheduler.sort_by_time(tasks) == [early, tie, late, untimed]
    assert tasks == [untimed, late, early, tie]
    assert scheduler.sort_by_time([]) == []


def test_filters_preserve_pet_and_task_identity():
    """Name/status filters work separately and together across pets."""
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    pending = Task("Walk", 5, "high")
    finished = Task("Walk", 5, "high", completed=True)
    cat_task = Task("Feed", 5, "high")
    dog.add_task(pending)
    dog.add_task(finished)
    cat.add_task(cat_task)
    scheduler = Scheduler(Owner("Jordan", 60, pets=[dog, cat]))
    assert scheduler.filter_tasks() == [(dog, pending), (dog, finished), (cat, cat_task)]
    assert scheduler.filter_tasks("Biscuit") == [(dog, pending), (dog, finished)]
    assert scheduler.filter_tasks(completed=True) == [(dog, finished)]
    assert scheduler.filter_tasks("Biscuit", False) == [(dog, pending)]
    assert scheduler.filter_tasks("Missing") == []
    pet, task = scheduler.filter_tasks("Biscuit", False)[0]
    assert pet is dog and task is pending


@pytest.mark.parametrize("recurrence,days", [("daily", 1), ("weekly", 7)])
def test_recurring_completion_and_history(recurrence, days):
    """Completion retains history, copies details, and creates one next occurrence."""
    pet = Pet("Biscuit", "dog")
    due = datetime(2026, 12, 31, 8, 30)
    original = Task("Care", 20, "high", due, recurrence)
    pet.add_task(original)
    next_task = pet.complete_task(original, due.date())
    assert original.completed and original.scheduled_time == due
    assert next_task is pet.tasks[1] and next_task is not original
    assert next_task.scheduled_time == due + timedelta(days=days)
    assert not next_task.completed
    assert (next_task.name, next_task.duration_minutes, next_task.priority, next_task.recurrence) == ("Care", 20, "high", recurrence)
    assert pet.complete_task(original, due.date() + timedelta(days=2)) is None
    assert len(pet.tasks) == 2


@pytest.mark.parametrize("recurrence,completion,expected", [
    ("daily", date(2026, 10, 14), datetime(2026, 10, 15, 8, 30)),
    ("weekly", date(2026, 10, 20), datetime(2026, 10, 25, 8, 30)),
    ("weekly", date(2026, 10, 18), datetime(2026, 10, 25, 8, 30)),
    ("weekly", date(2026, 10, 10), datetime(2026, 10, 18, 8, 30)),
])
def test_overdue_and_early_completion_preserve_cadence(recurrence, completion, expected):
    """Advance to the next cadence date after completion without overdue backlogs."""
    pet = Pet("Biscuit", "dog")
    original = Task("Care", 10, "high", datetime(2026, 10, 11, 8, 30), recurrence)
    pet.add_task(original)
    assert pet.complete_task(original, completion).scheduled_time == expected
    assert original.scheduled_time == datetime(2026, 10, 11, 8, 30)


def test_completion_one_off_and_wrong_pet():
    """One-offs create no successor and ownership checks use identity."""
    pet = Pet("Mochi", "cat")
    task = Task("Feed", 5, "high")
    pet.add_task(task)
    with pytest.raises(ValueError, match="belong"):
        pet.complete_task(Task("Feed", 5, "high"), date(2026, 10, 11))
    assert not task.completed
    assert pet.complete_task(task, date(2026, 10, 11)) is None
    assert task.completed and len(pet.tasks) == 1


@pytest.mark.parametrize("recurrence,scheduled", [
    ("monthly", datetime(2026, 10, 11, 8)), ("daily", None), ("weekly", None),
])
def test_recurrence_validation(recurrence, scheduled):
    """Reject unsupported recurrence and recurring tasks without a due time."""
    with pytest.raises(ValueError):
        Task("Care", 10, "high", scheduled, recurrence)


def test_future_recurrence_excluded_and_overdue_included():
    """Plans include unfinished due/overdue recurring tasks but exclude future ones."""
    pet = Pet("Mochi", "cat")
    overdue = Task("Overdue", 5, "high", datetime(2026, 10, 10, 8), "daily")
    future = Task("Future", 5, "high", datetime(2026, 10, 12, 8), "weekly")
    pet.tasks.extend([overdue, future])
    assert Scheduler(Owner("Jordan", 60, pets=[pet])).generate_daily_plan(date(2026, 10, 11)) == [overdue]


def test_cross_pet_conflicts_exclude_history_and_allow_back_to_back():
    """Default conflict detection spans pets, ignores history, and keeps times intact."""
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    first = Task("Walk", 30, "high", datetime(2026, 10, 11, 8))
    overlap = Task("Feed", 10, "high", datetime(2026, 10, 11, 8, 15))
    adjacent = Task("Play", 10, "high", datetime(2026, 10, 11, 8, 30))
    history = Task("History", 30, "high", first.scheduled_time, completed=True)
    dog.tasks.extend([first, history])
    cat.tasks.extend([overlap, adjacent, Task("Untimed", 5, "low")])
    scheduler = Scheduler(Owner("Jordan", 60, pets=[dog, cat]))
    assert scheduler.detect_conflicts() == [(first, overlap)]
    assert scheduler.detect_conflicts([first, adjacent]) == []
    assert first.scheduled_time == datetime(2026, 10, 11, 8)


def test_identical_start_times_produce_conflict():
    """Two distinct tasks starting at exactly the same time conflict."""
    start = datetime(2026, 10, 11, 8)
    first = Task("Walk", 30, "high", start)
    second = Task("Feed", 10, "medium", start)
    scheduler = Scheduler(Owner("Jordan", 60))
    assert scheduler.detect_conflicts([first, second]) == [(first, second)]


@pytest.mark.parametrize("with_pet", [False, True], ids=["no-pets", "pet-with-no-tasks"])
def test_empty_owner_schedules(with_pet):
    """Owners without pets or with a taskless pet have empty scheduling results."""
    owner = Owner("Jordan", 60)
    if with_pet:
        pet = Pet("Mochi", "cat")
        owner.add_pet(pet)
        assert pet.tasks == []
    scheduler = Scheduler(owner)
    assert owner.get_all_tasks() == []
    assert scheduler.filter_tasks() == []
    assert scheduler.generate_daily_plan(date(2026, 10, 11)) == []
    assert scheduler.detect_conflicts() == []


@pytest.mark.parametrize("budget,included", [(0, False), (19, False), (20, True)])
def test_daily_budget_boundaries_exclude_completed_tasks(budget, included):
    """A pending task fits exactly at its duration; completed work uses no budget."""
    due = datetime(2026, 10, 11, 8)
    done = Task("Completed care", 10, "high", due, completed=True)
    pending = Task("Walk", 20, "medium", due)
    pet = Pet("Biscuit", "dog", tasks=[done, pending])
    scheduler = Scheduler(Owner("Jordan", budget, pets=[pet]))
    plan = scheduler.generate_daily_plan(due.date())
    assert plan == ([pending] if included else [])
    assert sum(task.duration_minutes for task in plan) <= budget


def test_edit_preserves_owned_occurrence_and_changes_plan_selection():
    """Editing changes budget selection while retaining identity and recurrence details."""
    due = datetime(2026, 10, 11, 8)
    task = Task("Walk", 30, "low", due, "daily")
    pet = Pet("Biscuit", "dog", tasks=[task])
    other_pet = Pet("Mochi", "cat")
    scheduler = Scheduler(Owner("Jordan", 20, pets=[pet, other_pet]))
    assert scheduler.generate_daily_plan(due.date()) == []
    task.edit("  Short walk  ", 15, "high")
    assert (task.name, task.duration_minutes, task.priority) == ("Short walk", 15, "high")
    assert pet.tasks[0] is task and other_pet.tasks == []
    assert task.scheduled_time == due and task.recurrence == "daily" and not task.completed
    assert scheduler.generate_daily_plan(due.date()) == [task]
    successor = pet.complete_task(task, due.date())
    assert (successor.name, successor.duration_minutes, successor.priority) == ("Short walk", 15, "high")


@pytest.mark.parametrize("name,duration,priority", [
    ("  ", 15, "high"), ("Walk", 0, "high"), ("Walk", -1, "high"),
    ("Walk", 1.5, "high"), ("Walk", 15, "urgent"),
])
def test_invalid_edit_leaves_task_unchanged(name, duration, priority):
    """Invalid edits reject the whole update instead of partially changing the task."""
    task = Task("Original", 20, "medium", datetime(2026, 10, 11, 8), "daily", True)
    before = vars(task).copy()
    with pytest.raises(ValueError):
        task.edit(name, duration, priority)
    assert vars(task) == before
