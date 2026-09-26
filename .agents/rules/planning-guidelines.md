# Implementation Planning Guidelines

When working on this repository, strictly adhere to the following workflow for all major changes or new features:

## 1. Mandatory Plan Creation for Major Changes and New Features

Before modifying or creating code, you **must always create a detailed plan in a `.md` document** whenever a task involves:

- New features, pages, components, endpoints, or models.
- Major architectural changes or refactorings (e.g. schema renames, directory restructuring, state management changes).
- Multi-file edits spanning across backend and frontend.
- Non-trivial logic or behavior modifications.

**Do NOT start making code changes or running modifying commands before the plan document is created.**

## 2. Structure of the Implementation Plan

The `.md` plan must be clear and structured, containing:

1. **Goal / Overview**: Summary of what will be accomplished and why.
1. **Architecture & Design**: Detailed technical approach, data flow, types, schemas, and component structure.
1. **Proposed Changes**: Exact list of files to be created, modified, or deleted, grouped logically (backend, API, frontend components, styles, translations).
1. **Open Questions / User Review**: Any design decisions or ambiguities requiring user clarification or approval before execution.
1. **Verification Plan**: Step-by-step verification commands (`make react-lint`, `make react-build`, tests, manual verification steps).

## 3. Review and Approval

- Present the plan to the user clearly.
- Obtain user feedback or approval before proceeding to implementation.
- If unexpected complexities arise during implementation that alter the plan significantly, pause and update the plan for further review.
