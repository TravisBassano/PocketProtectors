---
layout: post
title: Draft Results
permalink: /draft/
---

<script id="draft-data" type="application/json">
  {{ site.data.draft-results | jsonify }}
</script>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="{{ '/assets/js/draft-scatter.js' | relative_url }}"></script>