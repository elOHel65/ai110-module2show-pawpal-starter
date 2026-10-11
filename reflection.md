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

AI suggested adding pet identification, availability windows,
recurring-task completion history, and explanations for skipped
tasks. I kept the initial skeleton simple and deferred these
changes. During implementation, I will define priority ordering
and tie-breaking so schedules are predictable.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
