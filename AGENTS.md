# Repository Guidelines

## Project Structure & Module Organization

This repository is an Arturo package named `sql`, intended as an SQL builder. It currently contains starter code: a `double` function and its specifications.

- `src/lib.art`: package library entry point; place reusable functionality here or in modules imported by it.
- `src/main.art`: executable entry point, currently demonstrating `double`.
- `specs/`: unit tests, discovered using the settings in `config.art`.
- `info.art`: package entry points, dependencies, and minimum Arturo version.
- `examples/`: location for runnable usage examples.
- `docs/icons/` and `docs/images/`: documentation assets.
- `.github/workflows/test.yml`: cross-platform test workflow.

## Build, Test, and Development Commands

Use Arturo 0.10.0 or newer, as required by `info.art`. Run commands from the repository root.

- `arturo -p install unitt`: install the test runner; package metadata requires Unitt 3.1.1 or newer.
- `unitt`: discover and run the specifications under `specs/`.
- `arturo src/main.art`: run the current executable demonstration.

Ensure Arturo's package binaries directory (`~/.arturo/packages/bin`) is on `PATH`. Windows CI invokes `cmd.exe /C unitt.bat`. No separate build, formatter, or lint command is configured.

## Coding Style & Naming Conventions

Follow the existing Arturo block syntax and use four spaces for new indentation. Existing `src/main.art` contains a tab; avoid introducing further indentation inconsistencies. Use descriptive lowerCamelCase names for new multiword identifiers and short, lowercase module filenames. Keep reusable logic in the library and executable behavior in `src/main.art`. Declare dependency or entry-point changes in `info.art`.

## Testing Guidelines

Use Unitt's `describe`, `it`, and `expects.be:` patterns, following `specs/lib.spec.art`. Name test files `*.spec.art`; discovery depends on this suffix. Add deterministic tests for new behavior and regressions, including relevant boundary cases. Run `unitt` and inspect its results before submitting. No coverage threshold is configured. CI tests Linux, macOS, FreeBSD, and Windows.

## Commit & Pull Request Guidelines

Git history currently contains only `Initial commit`, so no established commit convention exists. Use concise, imperative subjects describing the change. Keep pull requests focused, explain behavior changes, and include test commands and results. Link relevant issues when available and update documentation or examples when public usage changes.

## Agent Instructions

Read the available `arturo` skill's `SKILL.md` before writing, debugging, or testing Arturo code, or changing Arturo tooling. Consult its relevant references as needed for language semantics, packages, Unitt, and CI.
