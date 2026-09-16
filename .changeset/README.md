# Changesets for Research OS Studio

This directory contains configuration and pending changeset files for versioning and releasing the Research OS Studio skills suite.

## How it works

1. When introducing changes to skills (new skills, updates to prompts/templates, fixes), create a changeset by running:
   ```bash
   npx changeset
   ```
2. Select the change type (`patch`, `minor`, `major`) and describe the change.
3. Commit the generated `.changeset/*.md` file alongside your changes.
4. When merged to `main`, the Release workflow (`.github/workflows/release.yml`) uses `@changesets/action` to automatically manage version PRs and Git tags.
