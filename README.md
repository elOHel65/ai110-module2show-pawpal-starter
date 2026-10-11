# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

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
WARNING: Biscuit: Morning walk overlaps Mochi: Breakfast
Biscuit's tasks (pet filter)
2026-10-11 10:00 | Biscuit | Grooming | 20 min | medium | complete
2026-10-11 08:00 | Biscuit | Morning walk | 30 min | high | complete
2026-10-12 08:00 | Biscuit | Morning walk | 30 min | high | incomplete
2026-10-18 10:00 | Biscuit | Grooming | 20 min | medium | incomplete
Completed tasks (status filter)
2026-10-11 10:00 | Biscuit | Grooming | 20 min | medium | complete
2026-10-11 08:00 | Biscuit | Morning walk | 30 min | high | complete
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
collected 26 items

tests/test_pawpal.py ..........................                          [100%]

============================== 26 passed in 0.08s ==============================
```

The 26 test cases use fixed dates and cover task storage and completion,
collection across pets, chronological sorting of out-of-order input, pet/status
filters, daily and weekly recurrence (including an incomplete next-day task when
daily care is completed on its due date), recurrence and ownership validation,
and future-date exclusion. Conflict tests cover overlaps across pets, identical
start times, completed-history exclusion, and back-to-back intervals. Empty
owners and pets produce empty schedules. Budget tests cover zero available
minutes, one minute short, exact fits, skipping oversized tasks, and excluding
completed tasks from both plans and budget consumption.

**Confidence: 4/5 stars (★★★★☆)** for the tested backend scheduling behavior.
All automated tests pass, but automated backend tests do not guarantee every UI
behavior. This run did not check Streamlit forms, rendering, or session-state
interactions; browser/UI testing is still needed. Invalid durations/priorities
and timezone-aware scheduling are also outside this suite's coverage.

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

## System Design

### Core User Actions
1. Enter owner and pet information.
2. Add or edit care tasks with a duration and priority.
3. Generate a daily plan based on available time and priorities, with an explanation of the choices.
