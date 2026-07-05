---
type: playbook
description: How to roll back a bad release at Acme.
tags: [deploy, runbook]
---

Acme uses blue-green deployment: roll back by promoting the previous blue-green slot.

Steps: promote the previous slot, verify health checks, then announce in the
incident channel. Never patch forward during an active [[deploy-freeze]].
