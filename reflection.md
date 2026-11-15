# Reflection

**1. Which issues were the easiest to fix, and which were the hardest? Why?**

The easiest were the style issues from Flake8 and Pylint: unused imports, missing blank lines, long lines, snake_case names and `== False`. These were mechanical and the tools told me the exact line and fix. Removing `verify=False` and adding a timeout were also one-line changes.

The hardest were the logic bugs that no tool reported. I only found them by reading the program output: R01 showing 66% even though they attended every class, 75% being "not eligible", R02 being listed twice in the register, and the latest date being `2026-9-3`. Fixing them meant deciding what the program should actually do (holidays should not count, late is still present, one record per day, dates must be valid and not in the future). The mutable default argument was also tricky because fixing it changed how `main` got the shared register back.

**2. Did the static analysis tools report any false positives? If so, describe one example.**

Yes. Bandit flagged `scheduleReminders` (B604) for passing `shell=True`, but `runJob` only returns a dictionary and never runs a command, so nothing was actually executed in a shell. Bandit also reports `import subprocess` (B404) just for importing the module, even when it is used safely. Pylint's missing docstring warnings for very short obvious functions are more of a style preference than a real problem.

The tools also missed real problems: the hardcoded API key, the CSV formula injection in the student name, and all of the attendance calculation bugs.

**3. How would you integrate static analysis tools into your actual software development workflow?**

I would run Flake8 and Pylint in the editor while coding and add them, along with Bandit, as a pre-commit hook so problems are caught before a commit. In CI (for example GitHub Actions) every push and pull request would run all three tools and fail the build if Bandit finds a high-severity issue or the Pylint score drops below a set threshold. Since the tools do not catch logic errors, this should be combined with unit tests and code review.

**4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?**

The Pylint score went from 4.55/10 to 10.00/10, Flake8 reports no issues and Bandit went from 8 issues (2 high, 3 medium, 3 low) to none. The code is easier to read with consistent snake_case names, docstrings and simpler expressions. It is also more robust and secure: the API key is no longer in the source, certificate checks are on, requests can't hang, there is no shell command, the CSV can't carry formulas, and the file is always closed. Most importantly, the output is now correct: R01 shows 100%, R02 shows 25%, 75% counts as eligible, only R02 is in the shortage list, the register has no duplicates and the future date is rejected.
