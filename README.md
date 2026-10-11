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

Run the basic scheduling demo with `python main.py`:

```
08:00 | Biscuit | Morning walk | 30 min | high
09:00 | Mochi | Breakfast | 10 min | high
17:00 | Mochi | Playtime | 15 min | medium
```

## 🧪 Testing PawPal+

```bash
# Activate the virtual environment:
source .venv/bin/activate

# Run the full test suite:
python -m pytest

# Run with coverage (requires pytest-cov):
python -m pytest --cov
```

Actual test output from the basic scheduling phase:

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /root/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 6 items

tests/test_pawpal.py ......                                              [100%]

============================== 6 passed in 0.08s ===============================

tests/test_pawpal.py ...... [100%]
6 passed in 0.01s
```

The tests cover completion, task storage, collection across pets, priority/time
ordering, daily filtering and budget selection, and overlapping intervals.
Recurring tasks are considered as stored; occurrence expansion is deferred to
the smarter scheduling phase. Conflict detection reports overlapping pairs;
the basic plan does not resolve them or assign times to unscheduled tasks.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

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
