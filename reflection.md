# PawPal+ Project Reflection

## 1. System Design
Three core actions a user should be able to perform:

1. Add their pet’s information and care tasks, such as walks, feeding, or medication.
2. Set each task’s duration and priority, along with the time they have available.
3. Generate and view a daily care plan that explains which tasks were chosen.
**a. Initial design**
I chose four classes. Owner stores the owner's information and
available time. Pet stores pet information and care tasks.
Task represents a care activity with a duration and priority.
Scheduler organizes tasks into a daily plan using the owner's
constraints.
**b. Design changes**

I initially deferred advanced suggestions to keep the design
simple. Later, I added recurring-task completion history and
predictable priority/time ordering. Availability windows and
explanations for skipped tasks remain future improvements.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers available time, task priority, scheduled
dates, and completion status. Time and priority matter most
because owners need to fit important care tasks into a busy day.

**b. Tradeoffs**

Conflict detection checks every pair of tasks, taking O(n²) time.
This is easy to understand and reasonable for a small household
schedule, although it would be slower with many tasks.

---

## 3. AI Collaboration

**a. How you used AI**

I used Codex for class design, implementation, tests, UI integration,
and documentation. Specific prompts naming files and expected
behaviors were most helpful. Keeping phases in separate chats
helped organize the work.

**b. Judgment and verification**

I kept simple pairwise conflict detection instead of adopting a
more complex algorithm. I checked the CLI output and tried adding
a pet and task in the browser. Codex also reported passing tests.

---

## 4. Testing and Verification

**a. What you tested**

The suite checks sorting, filtering, completion, recurrence,
conflicts, time budgets, empty schedules, and editing. These tests
help catch incorrect schedules and unwanted changes to tasks.

**b. Confidence**
My confidence is 4/5 stars because all 33 tests passed. With more
time, I would test timezone handling, browser layout, and
accessibility.

---

## 5. Reflection

**a. What went well**

I am most satisfied with connecting the Python classes to a working
UI where users can manage tasks and generate a schedule.

**b. What you would improve**

I would add permanent storage so pet information survives new
sessions, then support availability windows and owner preferences.

**c. Key takeaway**
I learned that being the lead architect means choosing a clear
design and verifying AI-generated work. AI helped build the code,
but I still needed to review decisions and check the results.


---

## Review notes and suggested material (not completed reflection answers)

Existing answers in section 1 are preserved verbatim. Sections 2a–5c remain
unanswered. The suggestions below are for your review; choose your own wording
and add personal reasons or experiences only when they are true. Section 1b
also describes an earlier stage: the final code now implements recurrence
history and priority/time ordering, while availability windows and skipped-task
explanations remain deferred. Decide whether to add a retrospective note.

| Unanswered prompt | Suggested material to review |
| --- | --- |
| 2a. Constraints and priorities | The code considers available minutes, high/medium/low priority, scheduled date, recurrence, and completion status. Preferences are stored but unused. Explain in your own words why you chose those constraints. |
| 2b. Tradeoffs | Priority-first greedy selection skips tasks that do not fit and continues to smaller tasks. It is simple and predictable, but does not optimize the number of tasks or resolve overlaps. Review whether this tradeoff fits your intended scenario. |
| 3a. How you used AI | This conversation documents AI assistance with reviewing existing tests, adding missing edge cases, improving UI filters/feedback, and updating UML/documentation. Select the assistance you actually used and explain which prompts you found helpful. |
| 3b. Judgment and verification | Your section 1b documents deferring AI suggestions to keep the initial skeleton simple. If that is the example you want to use, explain your own reasoning. The recorded verification includes CLI execution, 26 passing backend cases, and a Streamlit AppTest smoke check; do not describe these as checks you personally ran unless you did. |
| 4a. What you tested | Recorded checks cover sorting, recurrence/history, conflicts, empty schedules, budgets, completed-task exclusion, and filters. These help catch ordering, duplicate-successor, overlap, and budget errors. Describe your own role accurately. |
| 4b. Confidence | Consider 4/5 stars for tested backend behavior, supported by 26 passing cases. Possible next checks include browser interactions, accessibility, invalid durations/priorities, and timezone handling. Decide your own confidence level. |
| 5a. What went well | Possible topics include preserving recurrence history, separating budget selection from display ordering, or adding repeatable edge-case tests. Choose what you are personally most satisfied with and explain why. |
| 5b. What you would improve | Options grounded in current limitations include permanent storage, task editing, clearer skip explanations, preferences/availability windows, or broader UI coverage. Choose your own next priority. |
| 5c. Key takeaway | Possible themes include translating requirements into edge cases, preserving task identity/history, and verifying AI-generated changes. State only a lesson you actually learned, with your own example. |
