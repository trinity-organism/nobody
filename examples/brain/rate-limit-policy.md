---
type: law
description: Default API rate limits protecting the platform and its SLA.
tags: [api, law]
verify: python3 -c "import pathlib; assert '99.9%' in pathlib.Path('customer-sla.md').read_text()"
---

The default API rate limit is 120 requests per minute per client.

Burst traffic beyond the limit receives HTTP 429. This law exists to protect the
[[customer-sla]]; its wall checks that the SLA it protects still states its number.
