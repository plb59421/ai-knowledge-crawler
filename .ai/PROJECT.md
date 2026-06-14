# AI Project Assets

This directory stores tool-neutral project assets for AI-assisted maintenance.

## Structure

- `prompts/`: Prompt templates used by runtime analysis.
- `skills/`: Project workflows and quality checks for crawler development.
- `knowledge/`: Domain policies, taxonomies, source profiles, and trust rules.
- `automation.yaml`: Tool-neutral automation tasks that can be loaded by external AI tools or converted into scheduler commands.

## Rules

- Do not store API keys, tokens, cookies, or private credentials here.
- Keep tool-specific integration files outside this directory unless they are generated from `automation.yaml`.
- Runtime secrets belong in `config/user.yaml`, which is ignored by Git.
