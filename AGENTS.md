# RL-ERP Development Rules

You are working on RL-ERP.

Technology Stack:

* FastAPI
* PostgreSQL
* SQLAlchemy 2.0
* Alembic
* Pydantic
* Docker

Development Principles:

1. Analyze before coding.
2. Create an implementation plan before making changes.
3. Wait for approval before coding major features.
4. Keep implementations simple and production-ready.
5. Follow existing repository patterns.
6. Prefer service-layer architecture.
7. Use SQLAlchemy 2.0 style syntax.
8. Create Alembic migrations for schema changes.
9. Update OpenAPI schemas when endpoints change.
10. Update tests when functionality changes.
11. Update documentation after every completed feature.

Branch Rules:

* Never work directly on main.
* Verify current branch before starting work.
* If implementing a new feature, recommend creating a feature branch.
* Do not create, merge, delete, push, or modify branches without approval.

Documentation Rules:

Whenever a feature is completed:

* Update README.md if user-facing behavior changed.
* Update docs/changelog.md.
* Update docs/roadmap.md.
* Update docs/project_state.md.
* Update docs/development_log.md.

Documentation Responsibilities

README.md
Purpose:
- Project overview
- Setup instructions
- Current major features
- API overview

Update When:
- New user-facing feature is added
- Setup process changes
- Architecture changes significantly

Never Store:
- Future plans
- Session notes
- Bug lists


docs/changelog.md
Purpose:
- Historical record of completed work

Update When:
- Feature completed
- Refactor completed
- Breaking change introduced

Format:

## YYYY-MM-DD

Added:
- Item

Changed:
- Item

Fixed:
- Item

Never Store:
- Future plans
- TODOs


docs/roadmap.md
Purpose:
- Planned future work

Update When:
- New feature planned
- Priority changes

Format:

Planned
In Progress
Completed

Never Store:
- Implementation details
- Session logs


docs/project_state.md
Purpose:
- Current snapshot of project

Update When:
- End of every development session

Contains:
- Completed modules
- In-progress modules
- Next priorities
- Known issues

Never Store:
- Detailed change history


docs/architecture.md
Purpose:
- System architecture

Update When:
- New module added
- Database design changes
- Major refactor

Contains:
- Module relationships
- Data flow
- Database design

Never Store:
- Session notes


docs/development_log.md
Purpose:
- Detailed engineering journal

Update When:
- Significant work completed

Contains:
- Why decisions were made
- Tradeoffs
- Technical notes

Never Store:
- Future roadmap items

Documentation Consistency Rule

Before updating documentation:

1. Determine which documentation files are affected.
2. Explain why each file requires modification.
3. Only update documentation that is directly impacted.
4. Do not duplicate information across files.

Feature Documentation Rule

For every completed feature:

1. Determine which documentation files are affected.
2. Explain why each file requires updates.
3. Update only the relevant documentation.
4. Summarize documentation changes before finishing the task.

Feature Completion Checklist

Before marking any feature as complete:

- Code implemented
- Tests updated
- API schemas updated
- Alembic migration created (if required)
- README reviewed
- changelog updated
- project_state updated
- roadmap updated
- architecture updated if system design changed
- development_log updated if technical decisions were made

Documentation File Ownership

README.md owns:
- Project overview
- Setup instructions
- Feature summary
- API overview

docs/changelog.md owns:
- Completed work history only

docs/roadmap.md owns:
- Future work
- Priorities
- Project phases

docs/project_state.md owns:
- Current status
- In-progress work
- Known issues
- Next priorities

docs/architecture.md owns:
- System architecture
- Database design
- Module relationships
- Data flow

docs/development_log.md owns:
- Engineering decisions
- Tradeoffs
- Technical implementation notes

Never place information into a file that is owned by another document.

Code Rules:

* Minimize comments.
* No dead code.
* No duplicated business logic.
* No hardcoded values.
* Prefer explicit typing.
* Keep solutions modular and scalable.


Git Rules:

* Never push to GitHub.
* Never commit automatically.
* Never merge branches automatically.
* Never rewrite git history.
* Never delete branches.

Instead:

1. Review git status.
2. Summarize changed files.
3. Explain what was modified.
4. Suggest logical commit groups.
5. Suggest commit messages.
6. Ask for approval before any git operation.

Session Start Procedure:

1. Read AGENTS.md.
2. Read README.md.
3. Read docs/project_state.md.
4. Read docs/roadmap.md.
5. Read docs/changelog.md.
6. Read docs/architecture.md.
7. Review git status.
8. Review recent commits.
9. Summarize current project state.
10. Identify unfinished work.
11. Recommend next steps.

Do not make changes during project review.

Feature Development Procedure:

Before coding:

1. Analyze repository structure.
2. Identify affected files.
3. Design database changes.
4. Design API changes.
5. Create implementation plan.
6. Explain risks.
7. Wait for approval.

End-of-Session Procedure:

1. Review completed work.
2. Determine which documentation files require updates.
3. Update only affected documentation.
4. Review git status.
5. Summarize all code changes.
6. Summarize all documentation changes.
7. Suggest commit messages.
8. Ask whether changes should be committed.

Never perform git commits, pushes, merges, rebases, resets, or branch deletions without explicit approval.

Safety Rule:

Before modifying more than 5 files:

1. List every file that will be modified.
2. Explain why each file requires changes.
3. Wait for approval.

Documentation Safety Rule:

Before modifying any documentation:

1. State which documentation files will be modified.
2. Explain why each file requires modification.
3. Do not update unrelated documentation.
4. Preserve historical records.
5. Preserve roadmap priorities unless explicitly changed.
6. Wait for approval if documentation changes are extensive.