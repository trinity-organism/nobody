---
type: concept
description: Release soak rules for the staging environment.
tags: [deploy, environments]
---

Every release must soak in the staging environment for 24 hours before production deployment.

Staging mirrors production data shape with synthetic records. Skipping the soak
requires an incident-level justification recorded in the [[postmortem-template]].
