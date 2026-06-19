---
name: review
description: Invoke the triage agent on the most recent advisory session and write a quality report to reports/
---

1. Read the most recent session data from the last run (available in memory or last output).
2. Invoke triage-agent with: user_input, allocation, explanation, and current timestamp.
3. Write the report to reports/triage_YYYYMMDD_HHMMSS.md using the current date and time.
4. Print a summary: overall score, pass/fail status, and any HIGH severity issues.
