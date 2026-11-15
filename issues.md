# Issues Found

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Hardcoded API key | Security (manual review) | 12 | `ERP_API_KEY` is written in the source, so anyone with the code has the live key. | Read it from the `ERP_API_KEY` environment variable. |
| SSL verification disabled | Security (Bandit B501, High) | 60 | `requests.post(..., verify=False)` turns off certificate checks, allowing man-in-the-middle attacks. | Removed `verify=False`. |
| Shell command with wildcard | Security (Bandit B602/B607/B609, B404) | 5, 64 | `subprocess.Popen("tar ... *.csv", shell=True)` runs through the shell and is open to wildcard injection. | Used the standard `tarfile` and `glob` modules instead, so `subprocess` is no longer needed. |
| CSV formula injection | Security (manual review) | 54, 77 | A student name like `=HYPERLINK(...)` is written to the CSV as-is and runs as a formula when opened in a spreadsheet. | Prefix values starting with `=`, `+`, `-` or `@` with `'` before writing. |
| Insecure TLS version | Security (Bandit B503, Medium) | 66 | `legacyChannel` defaults to `ssl.PROTOCOL_TLSv1`, which is outdated and insecure. | Default changed to `ssl.PROTOCOL_TLS_CLIENT`. |
| Request without timeout | Security / Reliability (Bandit B113, Pylint W3101, Medium) | 60 | `requests.post` has no timeout and can hang forever. | Added `timeout=10`. |
| `shell=True` passed to job | Security (Bandit B604, Medium) | 73 | `scheduleReminders` asks for the reminder job to run in a shell. | Call `run_job` with the default `shell=False`. |
| Mutable default argument | Bug (Pylint W0102) | 18 | `register={}` is shared between calls, so the register keeps old entries. | Default to `None` and create a new dict inside; `main` passes its own register. |
| 75% marked not eligible | Bug (manual review) | 30 | `isEligible` uses `>`, so a student with exactly 75% is wrongly in the shortage list. | Changed to `>=`. |
| Holidays counted as absent | Bug (manual review) | 23-27 | `H` (holiday) counts as a missed class and `L` (late) counts as absent, so R01 showed 66% instead of 100%. | Exclude `H` from the total and count `L` as present. |
| Duplicate attendance entries | Bug (manual review) | 18-21 | R02 was marked twice on 2026-09-01, inflating the record and the register. | Ignore a record if the student is already marked for that date. |
| Unvalidated / future dates | Bug (manual review) | 18-21, 45-47 | `"2026-9-3"` is stored as a different date and sorts after `"2026-09-04"`, so the latest date is wrong; a future date `2030-01-01` is accepted. | Parse dates with `datetime.strptime`, store them as ISO format, and reject future dates with `ValueError`. |
| Division by zero | Bug (manual review) | 27 | `attendancePercentage` crashes for a student with no records. | Return 0 when there are no records. |
| `shortageList` returns `None` | Bug (manual review) | 37-39 | Returns `None` instead of an empty list, which breaks callers that loop over it. | Always return a list. |
| File not closed safely, no encoding | Code quality (Pylint R1732, W1514) | 50 | `open()` without `with` or `encoding`, and without `newline=""` for CSV. | Use `with open(path, "w", newline="", encoding="utf-8")`. |
| Unused imports | Style (Pylint W0611, Flake8 F401) | 1, 4, 6 | `os`, `json` and `datetime` were imported but not used. | Removed `json`; `os` and `datetime` are now used. |
| Comparison to `False` | Style (Pylint C0121, Flake8 E712) | 35 | `== False` instead of `not`. | Use `not is_eligible(...)`. |
| Simplifiable if expression | Style (Pylint R1719) | 30 | `True if x else False` is redundant. | Return the comparison directly. |
| Unnecessary comprehensions | Style (Pylint R1721, R1729) | 43, 46 | List inside `any()` and a pointless nested comprehension. | Use generator expressions. |
| Naming style | Style (Pylint C0103) | 15-75 | Function names are camelCase instead of snake_case. | Renamed all functions to snake_case. |
| Missing docstrings | Style (Pylint C0114, C0116) | 1-75 | No module or function docstrings. | Added short docstrings. |
| Formatting | Style (Flake8 E302, E305, E501) | Many | Missing blank lines between functions and lines too long. | Added 2 blank lines and wrapped long lines. |
| No main guard | Code quality (manual review) | 96 | `main()` runs on import. | Wrapped in `if __name__ == "__main__":`. |
