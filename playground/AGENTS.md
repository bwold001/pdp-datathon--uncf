# Playground agent instructions

Explorer pages live in `client_application/src/app/(uncf-explorer)/uncf/` and their components in
`client_application/src/components/uncf/`. The server only mounts routers: Explorer numbers come
from the repo's `measures/` and `api/`, chat numbers from `analytics/` (see the root AGENTS.md).

Use [`pdp-data`](../.agents/skills/pdp-data/SKILL.md) only when mapping an original ARF field or
dictionary term to the modeled data. The data is synthetic: never present a value as a finding
about real students or institutions.
