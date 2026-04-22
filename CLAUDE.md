# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Status

This repository is currently empty — it contains only a `README.md` with the project title (`# trends-fetcher`) and has no source code, build configuration, dependency manifest, tests, or CI yet. There is a single commit (`Initial commit`) on `main`.

As a result, there is no architecture, no build/lint/test commands, and no established conventions to document. The project name implies a tool for fetching trend data, but no language, framework, or data source has been chosen yet.

## Guidance for Early Work

When scaffolding this project, update this file as soon as concrete choices are made. At minimum, add:

- The chosen language/runtime and package manager, and the commands to install, build, run, lint, and test (including how to run a single test).
- The entry point(s) and the high-level flow: what source the trends come from, how they're fetched, how they're transformed, and where they're written.
- Any external services or credentials required to run the fetcher locally.

Until the project has real structure, keep this file short rather than speculating.
