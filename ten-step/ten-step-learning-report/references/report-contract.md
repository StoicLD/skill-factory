# Report contract

## Template fields

Replace every occurrence of these placeholders in `assets/report-template.html`:

| Placeholder | Required content |
|---|---|
| `{{LANG}}` | BCP 47 language code such as `zh-CN` or `en` |
| `{{TOPIC}}` | HTML-escaped topic |
| `{{PROFILE}}` | One-line learner profile |
| `{{GENERATED_AT}}` | ISO date or clear local date |
| `{{METHOD_SUMMARY}}` | Two to four sentences describing the learning journey |
| `{{NAV_ITEMS}}` | Ten links targeting `#step-1` through `#step-10` |
| `{{STEP_SECTIONS}}` | Ten complete `<section>` elements |
| `{{SOURCES}}` | Normalized ordered list; each item uses `data-source` |
| `{{NEXT_ACTIONS}}` | Four copyable explicit Skill invocations |

Escape generated text before embedding it in HTML. Create links only from validated URLs. Do not put untrusted text into script blocks, event handlers, or raw SVG markup.

Build the output basename from the topic by replacing control characters and `< > : " / \ | ? *` with `-`, collapsing repeated separators, trimming trailing dots and spaces, and limiting the topic portion to 80 characters. Fall back to `ten-step-learning-report.html` when nothing safe remains.

## Step section contract

Give each step this structure:

```html
<section class="step" id="step-1" aria-labelledby="step-1-title">
  <p class="eyebrow">Step 01</p>
  <h2 id="step-1-title">Five-perspective inquiry</h2>
  <p class="purpose">Why this step matters.</p>
  <details class="panel input-panel">
    <summary>Input and upstream</summary>
    <div class="panel-body">Topic, profile fields, and named upstream artifacts.</div>
  </details>
  <div class="panel artifact-panel">
    <h3>Full artifact</h3>
    <div class="panel-body">Complete step output with inline citations.</div>
  </div>
  <aside class="takeaways" aria-label="Learning takeaways">
    <h3>Learning takeaways</h3>
    <ul><li>Three to five distilled conclusions.</li></ul>
  </aside>
</section>
```

Step-specific expectations:

- Step 1: five labeled perspective cards.
- Step 2: a readable conflict table or accessible SVG plus a textual equivalent.
- Step 5: five resource cards with canonical links and time estimates.
- Step 6: five-rung ladder plus the learner's estimated rung.
- Step 8: ten `<details>` question cards and five answer-free challenges.
- Step 10: short field sheet suitable for printing.

## Evidence contract

- Cite claims at the point of use with numbered links such as `[S3]`.
- Give every source-list item a unique `data-source="S3"` attribute.
- Include title, author or publisher, date when available, URL, access date, and the claim supported.
- Mark inference as inference. Do not cite a search-results page when a primary page is available.
- For an approved offline draft, use an "Unverified offline draft" banner and list missing evidence instead of fabricated citations.

## Continuation contract

The final section must show these exact Skill names and topic-aware examples:

- `$ten-step-06-learning-ladder`
- `$ten-step-07-core-sprint`
- `$ten-step-08-adaptive-exam`
- `$ten-step-09-feynman-loop`

Do not claim that selecting one will automatically invoke the next. The learner chooses each entry explicitly.

## Manual validation fallback

When the validator cannot run, verify:

1. No `{{...}}` placeholder remains.
2. IDs `overview`, `step-1` through `step-10`, `sources`, and `continue-learning` occur exactly once.
3. Navigation links resolve to those IDs.
4. No external stylesheet or script dependency exists.
5. All factual citations resolve to a source-list item.
6. Step 8 answers are concealed by default.
7. The four continuation Skill names are exact.
