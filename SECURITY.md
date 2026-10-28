# Security

## What runs

Katori's only executable code is `scripts/macros.py` inside each skill (one shared source at `shared/scripts/macros.py`). It uses the Python standard library, reads the CSV files next to it, reads JSON from standard input, and prints text. It makes no network calls, writes no files, and runs no other programs.

The plugin has no hooks, MCP servers, agents, or executables in `bin/`.

## Before you install any skill

Skills are instructions and code that Claude follows. Read them first, especially for skills from people you do not know. Everything here is plain text and readable source.

## Reporting a vulnerability

If you find a security problem (for example, a way the calculator could be made to read or write files it should not), please use GitHub's private vulnerability reporting on this repository (Security > Report a vulnerability) rather than a public issue. You can expect an acknowledgment within a week.
