# SQL Agent Failure Postmortem

## Query Asked
"Who is our best employee?"

## SQL the Agent Generated
```sql
SELECT e.first_name, e.last_name,
       SUM(od.unit_price * od.quantity * (1 - od.discount)) as total_revenue
FROM employees e
JOIN orders o ON e.employee_id = o.employee_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY e.first_name, e.last_name
ORDER BY total_revenue DESC
LIMIT 1
```

## What the Agent Returned
Margaret Peacock — presented confidently as the best employee.

## What Actually Happened
The query ran without errors and returned a plausible answer.
No warning was given. But the agent silently made a business
decision: it assumed "best" means highest revenue.

The full employee rankings tell a different story:

| Employee        | Orders | Revenue     |
|-----------------|--------|-------------|
| Margaret Peacock| 420    | $232,890.85 |
| Janet Leverling | 321    | $202,812.84 |
| Nancy Davolio   | 345    | $192,107.60 |

Nancy Davolio handled 345 orders vs Janet's 321 — so the
ranking for 2nd place flips depending on which metric you use.
"Best" is ambiguous and the agent never surfaced that ambiguity.

## Root Cause
The LLM resolved an ambiguous natural language term ("best")
by making a silent assumption (revenue = best) rather than:
- Asking the user for clarification, or
- Returning multiple metrics and letting the user decide

This is a **silent semantic failure** — the SQL is technically
valid, executes without errors, and returns a confident answer.
There is no signal to the user that an assumption was made.

## Why This is Dangerous in Production
In a real business context, "best employee" affects performance
reviews, bonuses, and promotions. An agent that silently picks
one metric and presents it as ground truth could lead to
consequential wrong decisions — with no error log to trace back.

## What LangSmith Showed
The LangSmith trace showed the sql_generate_node received the
ambiguous question and immediately mapped "best" to
ORDER BY total_revenue DESC with no intermediate reasoning step.
The format_answer_node then presented the result without
flagging the assumption made.

## The Fix
Two possible approaches:

**Option 1 — Clarification node:**
Add a node before sql_generate that detects ambiguous terms
("best", "worst", "top", "performing") and asks the user:
"By what metric? (revenue / order count / number of customers)"

**Option 2 — Multi-metric response:**
When ambiguous terms are detected, generate SQL that returns
multiple metrics and let the user interpret the result:
```sql
SELECT e.first_name, e.last_name,
       COUNT(o.order_id) as total_orders,
       SUM(od.unit_price * od.quantity * (1 - od.discount)) as total_revenue
FROM employees e
JOIN orders o ON e.employee_id = o.employee_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY e.first_name, e.last_name
ORDER BY total_revenue DESC;
```

## Lesson Learned
LLMs are pattern matchers — they will always resolve ambiguity
by picking the most statistically likely interpretation from
training data. "Best employee" → revenue is a reasonable guess,
but it is still a guess. Production agents need explicit
disambiguation strategies for business-critical queries.

The most transferable skill from this exercise: **always ask
what metric an ambiguous superlative maps to before writing SQL.**