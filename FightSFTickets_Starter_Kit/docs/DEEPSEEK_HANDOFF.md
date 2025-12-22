# DeepSeek Handoff

## Repository intent
This workspace was created as a **clean skeleton** for the FightSFTickets project.

Everything that existed previously has been preserved under:
- `miscellaneous/original_project_dump/`

Do not edit those files; treat them as reference.

## Work plan (recommended)
1. Read `miscellaneous/original_project_dump/00_READ_THIS_FIRST__...md` and docs 01–10.
2. Identify the “source of truth” in the polished code dump under:
   - `miscellaneous/original_project_dump/FightSFTickets_CODE_POLISHED/`
3. Rehydrate the code into this skeleton:
   - Move backend content into `backend/src/` modules
   - Move frontend content into `frontend/` modules
4. Replace placeholders with real implementations:
   - DB models + migrations
   - Payment provider integration
   - Admin/ops endpoints as needed
5. Keep running notes + decisions in `docs/DECISIONS.md`
6. Track tasks in `docs/TASK_QUEUE.md`

## Credentials
Human will supply credential file(s) under `credentials/`.
Never commit secrets.
