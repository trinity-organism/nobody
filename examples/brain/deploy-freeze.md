---
type: law
description: What is and is not allowed while a deploy freeze is active.
tags: [deploy, law]
verify: python3 -c "import pathlib; assert 'type: playbook' in pathlib.Path('rollback-procedure.md').read_text()"
---

During a deploy freeze, the only change type allowed is a rollback.

If an incident occurs during a freeze, execute the [[rollback-procedure]] immediately.
The wall of this law checks that the escape hatch exists and is a playbook.
