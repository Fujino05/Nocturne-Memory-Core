# Public Boundary

This repository is the reusable engine, not a mirror of the private household.

## Deliberately excluded

- `dashboard.html` and every private dashboard asset
- `opening.html` and its animation/art direction
- personal memory buckets, letters, dreams, traces, chat exports, and SQLite data
- private agent/human biographies and relationship prompts
- device tokens, SMTP credentials, API keys, webhook secrets, signing profiles
- hard-coded local filesystem paths and private service URLs
- the private Nocturne client application

## Kept for compatibility

Some internal schema keys predate this extraction (for example legacy anchor or
room labels). They are data-format compatibility names, not a bundled persona.
New visible prompt text and identity labels come from `identity.py` and local
environment variables.

## Release rule

Build public releases from this directory with fresh Git history. Do not merge
or publish the private repository history: deleted files remain recoverable from
Git history.

Before publishing:

1. run the test suite;
2. run `python scripts/public_audit.py`;
3. inspect `git status` and the staged diff;
4. confirm no real `buckets/`, `.env`, databases, images, or exports are tracked.
