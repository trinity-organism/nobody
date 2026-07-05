---
type: concept
description: How feature flags are managed at Acme.
tags: [deploy, tooling]
---

Acme manages feature flags with Flagsmith.

Flags default to off in production and are cleaned up within 30 days of full
rollout. Risky releases pair a flag with the [[rollback-procedure]].
