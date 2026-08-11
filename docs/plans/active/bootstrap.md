# Bootstrap plan

Status: initialized; ready for the first concrete Skill  
Started: 2026-08-11

## Completed in initialization

- Created an isolated product repository, Agent Context repository, and non-Git temporary directory.
- Established the portable core and host-adapter boundary.
- Defined the direct-child folder contract for independently distributable skills.
- Added a non-discoverable template, a zero-dependency scaffold command, a validator, and validator tests.
- Added quality gates and a current compatibility matrix.

## Next product work

1. Define one concrete Skill using positive and negative trigger examples.
2. Scaffold it with `python scripts/new_skill.py <name> --description "..."`.
3. Replace the generated workflow prompts with task-specific instructions and resources.
4. Validate structure, scripts, trigger behavior, and claimed host compatibility.

No first Skill is created by this bootstrap because no concrete workflow has been specified yet.

