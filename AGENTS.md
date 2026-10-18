# Repository guidelines

These instructions apply to all Python files in this repository. Keep the examples
easy to read, runnable independently, and focused on teaching Tkinter concepts.

## Formatting

- Follow PEP 8. Use four spaces per indentation level; never use tabs.
- Limit lines to 88 characters where practical. Wrap long expressions using
  parentheses rather than backslash continuations.
- Use double quotes for strings unless another form improves readability or
  avoids escaping. Use triple double quotes for docstrings.
- Leave two blank lines between top-level functions and classes, and one blank
  line between methods. Use blank lines sparingly to separate logical steps.
- Remove trailing whitespace, end files with a newline, and save files as UTF-8.
- Keep formatting consistent within each file. Avoid unrelated formatting changes.
- When available, use Ruff's formatter and import sorter for changed files:
  `python -m ruff check --select I --fix <files>` followed by
  `python -m ruff format <files>`. Do not add a formatter dependency solely to
  make a small change.

## Python style

- Group imports in this order: standard library, third-party packages, and local
  modules. Separate groups with a blank line and sort imports within each group.
- Prefer `import tkinter as tk` and explicit imports from `tkinter`.
  Do not use wildcard imports.
- Use `snake_case` for modules, functions, methods, and variables; `PascalCase`
  for classes; and `UPPER_SNAKE_CASE` for constants.
- Choose descriptive names. Short names are acceptable for small, obvious scopes.
  Do not rename existing scripts unless the task requires it.
- Prefer f-strings for interpolation and `pathlib.Path` for new filesystem code.
- Keep functions focused. Extract helpers when they clarify the example, but
  avoid unnecessary abstractions, frameworks, and dependencies.
- Add type hints to new or substantially changed functions where they clarify
  inputs and return values. Use syntax compatible with the project's supported
  Python version; do not raise the minimum version incidentally.
- Give each new demo a short module docstring explaining what it demonstrates
  and how to run it. Document public classes and non-obvious functions with
  concise docstrings. Comments should explain intent or constraints.
- Remove unused imports, unused variables, dead code, and commented-out code
  when working on the surrounding code.
- Use context managers for files and image resources. Specify `encoding="utf-8"`
  for text files unless the example requires another encoding.
- Catch specific exceptions. Do not use bare `except:` or silently suppress
  failures; present a useful message or deliberately handle the expected case.
- Resolve bundled assets relative to `__file__`, rather than the current working
  directory. Avoid machine-specific absolute paths.

## Tkinter conventions

- Put startup code in a `main()` function behind
  `if __name__ == "__main__":`. Importing a module must not create windows,
  start workers, or enter `mainloop()`.
- Prefer `ttk` widgets when their themed appearance suits the example. Use
  classic Tk widgets when their features are needed or are the topic being taught.
- Use clear widget and callback names. Keep widget creation, layout, and callback
  logic organized so the example is easy to follow.
- Do not mix `pack()` and `grid()` for children of the same parent. Configure
  expansion weights and fill behavior for resizable layouts.
- Keep long-running work off the GUI thread, except in an explicitly labeled
  demonstration of blocking behavior. Workers should communicate through a queue;
  perform Tk calls and widget updates on the GUI thread.
- Store recurring `after()` callback IDs and cancel pending callbacks when
  stopping, resetting, or closing. Prevent duplicate callback loops.
- Retain references to `PhotoImage` objects while widgets display them. Close
  image files after loading the data needed for display.
- Handle invalid input and filesystem failures with useful feedback. Keep the
  window usable after an error.

## Verification and scope

- Preserve the purpose and behavior of each demo during formatting-only work.
- Check syntax for changed Python files. If Ruff is available, check formatting
  and lint the changed files; fix issues introduced by the change.
- For behavior changes, exercise relevant GUI actions when a display is available,
  including window closure while timers or workers are active when applicable.
- Add focused regression tests for meaningful logic changes where practical.
  Formatting-only changes do not need new tests.
- Report which checks ran and any checks that could not be performed. Do not
  claim GUI behavior was tested when only syntax or static checks ran.
