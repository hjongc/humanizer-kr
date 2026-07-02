# Rewriting Playbook

Use this file when a Korean rewrite needs a specific edit strategy, not just a
general request to sound natural. The goal is a smaller, clearer sentence that
keeps the user's facts and reader relationship intact.

## Operating Rules

- Preserve facts, numbers, names, quotes, legal wording, and source claims.
- Remove only the pattern that weakens the sentence. Do not rewrite unrelated
  parts for polish.
- Keep the genre. A support reply should stay helpful; a notice should stay
  direct; documentation should stay scannable.
- If the source lacks the detail needed for a stronger sentence, keep the claim
  modest and ask for the missing detail instead of inventing it.

## Pattern Playbook

### Inflated Praise

Problem: broad praise such as `혁신적인`, `최적화된`, `강력한`, or `차별화된`
appears before evidence.

Edit: replace praise with the actual feature, current behavior, or verified
outcome. If no evidence exists, lower the claim.

Before: `혁신적인 기능으로 최적화된 사용자 경험을 제공합니다.`
After: `검색어를 입력하면 관련 문서를 한 화면에서 비교할 수 있습니다.`

### Translationese Connectors

Problem: `또한`, `이를 통해`, `나아가`, or `결과적으로` carries the flow
instead of the sentence itself.

Edit: remove the signpost or name the real relationship.

Before: `이를 통해 사용자는 필요한 정보를 더 빠르게 찾을 수 있습니다.`
After: `사용자는 필요한 정보를 더 빨리 찾습니다.`

### Honorific Padding

Problem: respect is expressed through ceremonial phrases such as
`사용자님께서는`, `확인하시어`, or `참고 부탁드립니다`.

Edit: keep politeness, but move the sentence toward the reader's next action.

Before: `아래 내용을 확인하시어 이용에 참고 부탁드립니다.`
After: `아래 내용을 확인해 주세요.`

### Weak Reader Action

Problem: a notice or support reply says `필요한 조치` or `진행해 주세요`
without naming the action.

Edit: name the action when it is present in the source. If not, keep the line
short and add a missing-detail note outside the rewrite.

Before: `확인한 뒤 필요한 조치를 진행해 주세요.`
After: `알림을 끄려면 설정에서 알림 옵션을 해제해 주세요.`

### Passive or Availability Chain

Problem: action disappears into `제공됩니다`, `저장됩니다`, `가능합니다`, or
`처리됩니다`.

Edit: name the actor when doing so is true and useful. In docs and support
copy, `할 수 있습니다` is allowed when it describes a capability without
repeating.

Before: `설정 변경이 가능하며 결과는 자동으로 저장됩니다.`
After: `설정을 바꾸면 시스템이 결과를 자동으로 저장합니다.`

### Change-Anchored Documentation

Problem: product docs describe history with `추가되었습니다`, `개선되었습니다`,
or `변경되었습니다` when the reader needs the current behavior.

Edit: write the current state. Keep change wording only in changelogs,
migration guides, and release notes.

Before: `자동 저장 기능이 추가되었습니다.`
After: `입력한 내용은 자동으로 저장됩니다.`

### Chatbot Artifacts

Problem: assistant scaffolding such as `좋은 질문입니다`, `물론입니다`, or
`아래와 같이 정리해 드립니다` remains in public copy.

Edit: remove the scaffold and start with the useful sentence.

Before: `좋은 질문입니다. 아래와 같이 정리해 드립니다. 알림은 설정에서 끌 수 있습니다.`
After: `알림은 설정에서 끌 수 있습니다.`

### Over-Structured Formatting

Problem: headings, bold labels, or three-part lists make a short message feel
like a chatbot answer.

Edit: keep structure only when it helps scanning. Otherwise use one sentence,
plain bullets, or a small table.

Before: `- **속도:** 페이지 속도가 개선되었습니다.`
After: `- 페이지가 더 빨리 열립니다.`

### Voice Match

Problem: a rewrite becomes generically polished and loses the user's voice.

Edit: use the provided sample as the stronger constraint. Preserve sentence
length, ending style, and tolerance for roughness unless it hides meaning or
breaks a required public register.

### Over-Editing

Problem: the rewrite adds a benefit, metaphor, example, emotional color, or
institution that the source did not provide.

Edit: remove the added material. If the sentence needs evidence, ask for it
outside the rewrite.

