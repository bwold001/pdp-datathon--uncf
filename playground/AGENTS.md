# Playground agent instructions

When developing an institution-focused feature in Sandbox, use the normalized data model and follow
[`pdp-sandbox`](../.agents/skills/pdp-sandbox/SKILL.md). Use
[`pdp-data`](../.agents/skills/pdp-data/SKILL.md) only when mapping an original ARF field or
dictionary term to the modeled data.

For the deployment boundary and synthetic-data language, follow `pdp-sandbox`; do not treat
invented values as results from the shared model.
