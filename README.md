# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app for planning care tasks across multiple pets.

## Features

- Save owner availability and multiple pets in the current session.
- Add tasks with duration, priority, optional date/time, and None/daily/weekly recurrence.
- Edit an existing task's title, duration, and priority with input validation, preserving its pet association.
- Filter saved tasks by pet name and completion status; display tasks chronologically with unscheduled tasks last.
- Generate a daily plan using high/medium/low priority and the available-minute budget, then display it chronologically.
- Warn about overlapping incomplete tasks with pet names, task names, and scheduled times.
- Complete tasks while retaining history and creating one next recurring occurrence.
- Verify core scheduling behavior with repeatable backend tests.

Preferences and care needs are stored in the model but do not influence scheduling.
Permanent storage, automatic conflict resolution, and per-task
skip explanations are not implemented.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Run

Use Python 3.10 or newer. After setup, keep the virtual environment activated
and run these commands from the project root:

```bash
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`).
For the terminal demo or backend tests:

```bash
python main.py
python -m pytest
```

If your system provides only `python3`, use `python3 -m venv .venv` for the
initial setup; activation makes `python` available inside the environment.

## 🖥️ Sample Output

Run the smarter scheduling demo with `python main.py`. Actual output from
2026-10-11 (America/Los_Angeles):

```
Today's Schedule
2026-10-11 08:00 | Biscuit | Morning walk | 30 min | high | incomplete
2026-10-11 08:15 | Mochi | Breakfast | 10 min | high | incomplete
2026-10-11 10:00 | Biscuit | Grooming | 20 min | medium | incomplete
2026-10-11 17:00 | Mochi | Playtime | 15 min | medium | incomplete
Conflicts across pets
WARNING: Biscuit: Morning walk (2026-10-11 08:00) overlaps Mochi: Breakfast (2026-10-11 08:15)
Biscuit's tasks (pet filter)
2026-10-11 08:00 | Biscuit | Morning walk | 30 min | high | complete
2026-10-11 10:00 | Biscuit | Grooming | 20 min | medium | complete
2026-10-12 08:00 | Biscuit | Morning walk | 30 min | high | incomplete
2026-10-18 10:00 | Biscuit | Grooming | 20 min | medium | incomplete
Completed tasks (status filter)
2026-10-11 08:00 | Biscuit | Morning walk | 30 min | high | complete
2026-10-11 10:00 | Biscuit | Grooming | 20 min | medium | complete
Biscuit's next occurrences (both filters)
2026-10-12 08:00 | Biscuit | Morning walk | 30 min | high | incomplete
2026-10-18 10:00 | Biscuit | Grooming | 20 min | medium | incomplete
```

## 🧪 Testing PawPal+

```bash
source .venv/bin/activate
python -m pytest
```

Actual test results:

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /root/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 33 items

tests/test_app.py .                                                      [  3%]
tests/test_pawpal.py ................................                    [100%]

============================== 33 passed in 0.92s ==============================
```

The 32 backend test cases use fixed dates and cover task storage and completion,
collection across pets, chronological sorting of out-of-order input, pet/status
filters, daily and weekly recurrence (including an incomplete next-day task when
daily care is completed on its due date), recurrence and ownership validation,
and future-date exclusion. Conflict tests cover overlaps across pets, identical
start times, completed-history exclusion, and back-to-back intervals. Empty
owners and pets produce empty schedules. Budget tests cover zero available
minutes, one minute short, exact fits, skipping oversized tasks, and excluding
completed tasks from both plans and budget consumption. Editing tests verify
that valid updates affect plan selection, retain ownership and recurrence, and
reject invalid inputs without partial changes. A separate Streamlit test verifies
selection, validation feedback, saving edits, and state across reruns (33 total cases).

**Confidence: 4/5 stars (★★★★☆)** for the tested backend scheduling behavior.
All automated tests pass, but automated backend tests do not guarantee every UI
behavior. A Streamlit AppTest smoke check verified pet/task form submission, recurrence
selection, pet/status filters, conflict warnings, plan generation, completion
feedback, and session state across reruns. This does not verify browser layout,
accessibility, or every UI interaction; browser testing is still needed. Invalid durations/priorities at initial backend task construction and
timezone-aware scheduling are outside this suite's coverage.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | Select high/medium/low priority first; display chronologically with unscheduled tasks last. |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.generate_daily_plan()` | Exact pet name and/or completion filters return `(Pet, Task)` pairs; plans skip completed and future occurrences and continue past tasks that exceed the remaining budget. |
| Conflict handling | `Scheduler.detect_conflicts()` | Defaults to incomplete tasks across all pets; returns overlapping task pairs. Touching boundaries are allowed. CLI/UI warnings identify pets; no times are changed. |
| Recurring tasks | `Task.__post_init__()`, `Pet.complete_task()` | Validate None/daily/weekly, require recurring due times, preserve history, and create one next occurrence. Repeated completion is a no-op. |

### Sorting and task ownership

`sorted(tasks, key=lambda task: (...))` returns a new list without changing the
input. The lambda computes a comparison key for each task. In `sort_by_time()`,
that key is `(task.scheduled_time is None, task.scheduled_time)`: `False` sorts
before `True`, so dated tasks come first, then their datetimes determine order.
Equal keys preserve input order. Priority selection uses `sort_tasks()` before
budget allocation; `sort_by_time()` only orders the selected tasks for display.

Zero-padded 24-hour `HH:MM` strings sort chronologically within a single day
because hours and minutes have fixed widths (for example, `08:05` precedes
`10:00`). We retain datetime values because they also carry dates and support
interval comparisons and recurrence arithmetic. UI/CLI inputs use local naive
datetimes; the demo's definition of today uses America/Los_Angeles.

Filtering preserves actual pet/task objects in `(Pet, Task)` pairs, so callers
can identify ownership even when task names repeat. `None` means no filter;
`completed=False` means incomplete only. Duplicate pet names match every pet
with that exact name. `Owner.get_all_tasks()` still supplies daily-plan tasks.

### Recurrence policy

Use `Pet.complete_task(task, completion_date)` for user-facing completion. It
checks ownership by identity, keeps the completed original, and appends a new
incomplete Task with the same name, duration, priority, and recurrence. A task
due on the completion day advances by `timedelta(days=1)` for daily recurrence
or `timedelta(days=7)` for weekly recurrence, preserving its scheduled clock
time. One-off tasks create no successor. `Task.mark_complete()` remains the
low-level flag setter called by the recurrence-aware operation.

For overdue recurring tasks, skip missed dates and create the first occurrence
on the original cadence strictly after the completion day. For example, a weekly
task due Sunday October 11 and completed Tuesday October 20 advances to Sunday
October 25 at the original clock time. Early completion advances once from the
original due date. Completing the same original again creates no duplicate.
Only one pending successor is created, rather than expanding a backlog.

Daily plans include overdue unfinished recurring occurrences using their actual
stored date, exclude future recurring occurrences, and include one-offs only on
their scheduled date (or when unscheduled). Completion does not silently move
the historical task's time. Conflict detection reports stored intervals, not
hypothetical rescheduled slots. Unscheduled tasks have no interval to compare.

### Algorithm review

`detect_conflicts()` checks each pair once and compares half-open intervals:
`first_start < second_end and second_start < first_end`. The strict comparisons
make back-to-back tasks valid. This is easy to read and works across pets;
completed history is excluded in the default call. It costs O(n²) comparisons
and O(k) output space for k reported conflicts, which is reasonable for a small
household schedule.

One alternative is a sweep over tasks sorted by start time, maintaining active
intervals ordered by end time. Expire intervals ending at or before the next
start and report overlaps with the remaining active tasks. With suitable data
structures this costs O(n log n + k), but adds sorting and active-set management
that is harder to read and test. Dense schedules can still produce O(n²)
conflicts. The current implementation is retained; this alternative is a choice
for a later change, not an automatic replacement.

Session state retains the Owner, pets, tasks, and completion history between
Streamlit reruns in the current session. It is not permanent storage; a new
session or server restart can lose this data.

## 📸 Demo Walkthrough

1. Start the app, enter an owner name, and set the daily budget to 90 minutes. Add Biscuit (dog) and Mochi (cat).
2. Select Biscuit and add Morning walk: 30 minutes, high priority, daily recurrence, scheduled today at 08:00. Add Mochi's Breakfast: 10 minutes, high priority, no recurrence, today at 08:15. Add a later task before an earlier one to see chronological ordering.
3. In Edit a task, choose Morning walk. Change its title to Morning care, duration to 25 minutes, and priority to medium, then click Save Changes. Confirm the success message and updated table. Blank titles are rejected and durations must be positive whole numbers. Edits affect only the selected occurrence; its pet, date/time, recurrence, and completion status stay unchanged. Restore the original values if you want to follow the example below exactly.
4. In Saved pets and tasks, select a pet and choose All, Incomplete, or Completed. The table uses both filters. Return to All pets / All to view everything.
5. Choose today's Plan date and click Generate Plan. Tasks are selected by priority within the budget and displayed in chronological order, with unscheduled tasks last. The caption shows selected minutes. Table filters do not change the plan.
6. Inspect Conflict warnings: Biscuit's Morning walk at 08:00 overlaps Mochi's Breakfast at 08:15. Warnings check all saved incomplete tasks, including tasks outside the selected plan. They do not move or remove tasks.
7. Set Completion date to today and click Complete for Morning walk. A success message reports the next occurrence. Filter Completed to see the original and Incomplete to see tomorrow's walk at 08:00. Pets, tasks, and history remain available through reruns in the current session.

## System Design

The [final UML](diagrams/uml_final.mmd) lists the backend's attributes, methods,
and relationships. The [original working diagram](diagrams/uml_draft.mmd) is
preserved unchanged. It already contains the four classes and scheduling methods;
the final diagram adds Task.edit() and makes the scheduler's dependency on Pet explicit.
Owner aggregates pets, Pet aggregates tasks, and Scheduler references Owner and
uses Pet/Task objects for filtering and planning. `diagrams/uml.mmd` now mirrors
the final diagram instead of containing template classes.


### Core User Actions
1. Enter owner and pet information.
2. Add care tasks with a duration, priority, optional time, and recurrence.
3. Generate a daily plan based on available time and priorities, inspect conflicts, and complete tasks.
