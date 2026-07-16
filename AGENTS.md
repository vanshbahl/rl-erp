# RL-ERP Development Rules

You are working on RL-ERP.

Technology Stack:

* FastAPI
* PostgreSQL
* SQLAlchemy 2.0
* Alembic
* Pydantic
* Docker
* React 19 (Vite)
* Tailwind CSS v4
* Zustand & React Query

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
* Update PRD.md if product requirements or features changed.
* Update TRD.md if architecture or tech stack changed.
* Update UI_UX_Design.md if design systems changed.
* Update App_Flow.md if workflows or state machines changed.
* Update Backend_Schema.md if database schema or API structures changed.
* Update Developer_Guide.md if setup instructions or coding patterns changed.

Documentation Responsibilities

README.md owns:
- Project overview and tech stack
- High-level architecture
- Setup instructions
- Links to core documentation

PRD.md owns:
- Product vision, goals, and user stories
- Target users and feature lists
- Non-goals and acceptance criteria

TRD.md owns:
- System architecture details and deployment patterns
- State management and security flows
- Scaling and performance considerations

UI_UX_Design.md owns:
- Design philosophy and visual identity
- Typography, spacing, and animations
- Component states (loading, empty, error)

App_Flow.md owns:
- User workflows and flow diagrams
- Order, production, and invoice state machines
- Error handling flows

Backend_Schema.md owns:
- Database ERD and table definitions
- Enums, constraints, and migrations
- Service logic documentation

Developer_Guide.md owns:
- Local setup and environment variables
- Coding standards and folder conventions
- Git workflow and testing strategy

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
- PRD updated (if features changed)
- TRD updated (if architecture changed)
- UI_UX_Design updated (if frontend changed)
- App_Flow updated (if flows changed)
- Backend_Schema updated (if DB changed)
- Developer_Guide updated (if setup changed)



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
3. Read PRD.md to understand the product vision.
4. Read App_Flow.md and TRD.md to understand the current architecture.
5. Read Backend_Schema.md if working on the database.
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