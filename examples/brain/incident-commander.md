---
type: role
description: The immortal role that owns incident response end to end.
tags: [orchestration, incidents]
charter: May declare, run and close incidents, and freeze deploys during one.
owes: A blameless postmortem for every closed incident.
heir: release-captain
---

Mutual succession with [[release-captain]]: each is the other's heir, so no
incident or release is ever orphaned between sessions. Writes its lessons via
the [[postmortem-template]].
