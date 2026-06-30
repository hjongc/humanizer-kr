# Humanizer KR

[English](README.en.md) | 한국어

AI가 쓴 것처럼 보이는 한국어 초안을 더 자연스럽고, 문맥에 맞고, 읽는 사람에게 맞는 문장으로 다듬는 CodexㆍClaude Code용 글쓰기 스킬입니다.

Humanizer KR는 한국어 문장에서 자주 보이는 번역투, 과한 홍보 문구, 명사화, 수동 표현, 어색한 높임, 챗봇식 전개를 찾아 고칩니다. 사실, 의도, 문단 흐름, 말투는 보존하고 표현만 바꾸는 것을 원칙으로 합니다.

AI 탐지기가 아닙니다. 표절을 숨기거나, 다른 사람이 쓴 것처럼 꾸미거나, 학업ㆍ채용ㆍ심사 절차를 우회하는 용도로 쓰면 안 됩니다.

## 설치

### Codex 플러그인

권장 방식은 GitHub marketplace를 추가한 뒤 플러그인을 설치하는 흐름입니다.

```bash
codex plugin marketplace add hjongc/humanizer-kr --ref v0.1.4
codex plugin add humanizer-kr@humanizer-kr-marketplace
```

설치 후 Codex를 재시작하면 `$humanizer-kr`로 사용할 수 있습니다.

```text
Use $humanizer-kr to make this Korean draft sound natural:
[고칠 한국어 초안]
```

### Claude Code 플러그인

Claude Code에서는 HTTPS GitHub URL을 쓰는 방식을 권장합니다. `owner/repo` 형식은 환경에 따라 SSH clone을 시도할 수 있습니다.

```bash
claude plugin marketplace add https://github.com/hjongc/humanizer-kr.git
claude plugin install humanizer-kr@humanizer-kr-marketplace
```

Claude Code에서는 보통 아래처럼 네임스페이스를 붙여 호출합니다.

```text
/humanizer-kr:humanizer-kr
```

태그를 고정해서 쓰고 싶다면 로컬에 태그를 지정해 clone한 뒤 그 경로를 marketplace로 추가하세요.

```bash
git clone --branch v0.1.4 https://github.com/hjongc/humanizer-kr.git
claude plugin marketplace add ./humanizer-kr
claude plugin install humanizer-kr@humanizer-kr-marketplace
```

### 수동 설치

플러그인 metadata 없이 스킬만 쓰려면 스킬 폴더를 Codex 스킬 디렉터리에 복사합니다.

```text
skills/humanizer-kr/ -> ~/.codex/skills/humanizer-kr/
```

## 사용법

설치된 스킬을 명시해서 초안을 붙여 넣습니다.

```text
Use $humanizer-kr to make this Korean draft sound natural:
[고칠 한국어 초안]
```

AI 문체만 리뷰할 수도 있습니다.

```text
Use $humanizer-kr to review this Korean copy for AI-like phrasing:
[검토할 한국어 문장]
```

### 문체 맞추기

사용자의 기존 한국어 글 샘플을 함께 주면 문장 길이, 어미, 리듬, 표현 습관을 참고합니다. 일반적인 "깔끔한 한국어"로 덮어쓰지 않고, 샘플의 목소리를 우선합니다.

```text
Use $humanizer-kr. Match this sample voice:
[내가 쓴 한국어 샘플 2-3문단]

Rewrite this:
[고칠 초안]
```

## 개요

Humanizer KR는 영어권 AI 문체 목록을 그대로 번역한 스킬이 아닙니다. 한국어에서 실제로 어색하게 보이는 패턴을 중심으로 구성했습니다.

특히 아래 상황에 맞춰 만들었습니다.

- 제품 카피처럼 짧은 문장에서 과장 표현이 신뢰를 깎는 경우
- 공지문이나 지원 이메일에서 높임이 과해져 핵심 안내가 흐려지는 경우
- 제안서나 보고서에서 근거 없는 효과, 모호한 권위, 헤징이 겹치는 경우
- 문서나 릴리즈 노트가 현재 동작이 아니라 "무엇이 바뀌었는지"만 설명하는 경우
- 소셜 포스트가 슬로건 리듬과 챗봇식 친절함으로 평평해지는 경우

스킬은 초안을 읽고, 장르와 독자를 먼저 정한 뒤, 사실과 문단 범위를 유지하면서 문장만 다시 씁니다. 근거가 약한 주장은 더 작게 말하거나 출처를 요청합니다.

### 핵심 관점

LLM은 가장 무난하고 넓게 맞아 보이는 문장을 고르는 쪽으로 기울기 쉽습니다. 한국어에서는 그 결과가 `또한`, `이를 통해`, `혁신적인`, `최적화된`, `가능합니다`, `기대됩니다` 같은 표현의 반복으로 나타나는 경우가 많습니다.

Humanizer KR는 이런 표현을 단어 하나만 보고 지우지 않습니다. 여러 신호가 함께 모여 문장을 딱딱하게 만들 때 고칩니다.

## 20개 패턴

| # | 패턴 | Before | After |
| --- | --- | --- | --- |
| 1 | 번역투 연결어 | `또한, 이를 통해 사용자는 더 나은 경험을 얻을 수 있습니다.` | `사용자는 더 빨리 찾고 덜 헤맵니다.` |
| 2 | 과한 홍보 표현 | `혁신적인 기능으로 최적화된 사용자 경험을 제공합니다.` | `검색어를 입력하면 관련 문서를 한 화면에서 비교할 수 있습니다.` |
| 3 | 명사화된 표현 | `업무 효율성 향상을 위한 자동화 기능 제공이 가능합니다.` | `반복 업무를 자동으로 처리해 시간을 줄입니다.` |
| 4 | 수동ㆍ가능 표현 반복 | `설정 변경이 가능하며 결과는 자동으로 저장됩니다.` | `설정을 바꾸면 시스템이 결과를 자동으로 저장합니다.` |
| 5 | 모호한 권위 | `많은 전문가들은 이 방식이 중요하다고 말합니다.` | `이 방식은 장애 지점을 로그에서 바로 확인할 때 유용합니다.` |
| 6 | 챗봇식 구조화 | `## 핵심 요약\n사용 방법은 다음과 같습니다.` | `## 사용 방법\n먼저 계정을 만듭니다.` |
| 7 | 말투 흔들림 | `확인합니다. 다음 단계로 넘어가요. 사용자는 저장해야 한다.` | `확인합니다. 다음 단계로 이동합니다. 사용자는 저장합니다.` |
| 8 | 영어 우선 단어 | `핵심 인사이트와 니즈를 기반으로 어프로치를 설계합니다.` | `사용자가 실제로 겪는 문제를 기준으로 접근 방식을 정합니다.` |
| 9 | 괄호ㆍ기호 과밀 | `사용자(관리자/운영자)의 업무 효율(생산성)을 높입니다.` | `관리자와 운영자의 반복 업무를 줄입니다.` |
| 10 | 챗봇 답변 흔적 | `물론입니다. 아래와 같이 정리해 드립니다.` | `아래 내용을 확인해 주세요.` |
| 11 | 과한 높임 | `사용자님께서는 확인하시어 이용에 참고 부탁드립니다.` | `아래 내용을 확인해 주세요.` |
| 12 | 근거 부족 회피문 | `정보는 제한적이지만 중요한 역할을 한 것으로 보입니다.` | `현재 초안에는 역할을 확인할 근거가 없습니다.` |
| 13 | 포괄적 긍정 결론 | `앞으로의 행보가 기대됩니다.` | `다음 업데이트에서는 검색 필터와 저장 기능을 먼저 개선합니다.` |
| 14 | 헤징 과다 | `상당히 긍정적인 영향을 줄 수 있을 것으로 보입니다.` | `반복 입력 시간을 줄일 수 있습니다.` |
| 15 | 제목 뒤 워밍업 | `## 설정\n설정 방법을 살펴보겠습니다.` | `## 설정\n알림을 끄려면 설정에서 알림 옵션을 해제합니다.` |
| 16 | 굵은 라벨 목록 | `- **속도:** 속도가 개선되었습니다.` | `- 페이지가 더 빨리 열립니다.` |
| 17 | 가짜 솔직함 | `솔직히 말하면, 핵심은 사용자가 쉽게 이해하는 것입니다.` | `사용자가 바로 이해할 수 있어야 합니다.` |
| 18 | 동의어 돌려쓰기 | `사용자는 저장하고, 고객은 확인하며, 이용자는 알림을 받습니다.` | `사용자는 설정을 저장하고 결과와 알림을 확인합니다.` |
| 19 | 변경 내역 앵커 | `기존 방식 대신 새롭게 추가된 자동 저장 기능입니다.` | `입력한 내용은 자동으로 저장됩니다.` |
| 20 | 슬로건 리듬 | `빠릅니다. 간단합니다. 강력합니다.` | `기본 템플릿으로 시작하고, 팀이 자주 쓰는 항목만 나중에 추가할 수 있습니다.` |

## 전체 예시

**Before**

> 안녕하세요. 좋은 질문입니다. 아래와 같이 정리해 드립니다.
>
> 사용자님께서는 설정 메뉴에 접속하시어 알림 옵션을 확인하시고, 필요하신 경우 변경 진행 부탁드립니다. 또한 해당 이슈는 온보딩 과정에서 발생할 수 있는 부분이므로 이용에 참고 부탁드립니다.

**Draft rewrite**

> 안녕하세요.
>
> 설정 메뉴에서 알림 옵션을 확인해 주세요. 필요하면 알림 설정을 바꿀 수 있습니다.
>
> 이 문제는 처음 설정할 때 발생할 수 있습니다. 계속 문제가 생기면 다시 문의해 주세요.

**아직 어색한 점**

- `필요하면 알림 설정을 바꿀 수 있습니다`는 가능 표현이 남아 있어 안내가 조금 흐립니다.
- `다시 문의해 주세요`는 사용자가 무엇을 보내야 하는지 알려 주지 않습니다.
- 원문에 있던 `이슈`, `온보딩`, `참고 부탁드립니다` 같은 표현은 줄었지만, 지원 이메일로는 마지막 문장이 조금 덜 구체적입니다.

**Final**

> 안녕하세요.
>
> 설정 메뉴에서 알림 옵션을 확인해 주세요. 알림을 받고 싶지 않다면 해당 옵션을 끄면 됩니다.
>
> 이 문제는 처음 설정할 때 자주 발생합니다. 같은 문제가 계속되면 오류 화면을 함께 보내 주세요.

바뀐 점: 챗봇식 시작 문장을 걷어내고, 과한 높임을 줄였으며, `이슈`와 `온보딩`을 일반 사용자가 바로 이해할 수 있는 말로 바꿨습니다. 마지막 문장은 사용자가 다음에 무엇을 보내야 하는지까지 남겼습니다.

## 로컬 감사 스크립트

스킬에는 패턴 감사 스크립트가 포함되어 있습니다. 이 스크립트는 문장을 고치지 않고 검토할 표현만 표시합니다. 어떤 글이 AI가 쓴 글인지 증명하지 않습니다.

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py path/to/draft.md
```

표준 입력도 사용할 수 있습니다.

```bash
printf '또한 본 솔루션은 혁신적인 경험을 제공합니다.' | python3 skills/humanizer-kr/scripts/audit_korean_text.py
```

JSON 출력:

```bash
python3 skills/humanizer-kr/scripts/audit_korean_text.py --json path/to/draft.md
```

## 예시 파일

| 장르 | Before | After |
| --- | --- | --- |
| 제품 카피 | `examples/product-copy.before.ko.md` | `examples/product-copy.after.ko.md` |
| 공지문 | `examples/public-notice.before.ko.md` | `examples/public-notice.after.ko.md` |
| 지원 이메일 | `examples/support-email.before.ko.md` | `examples/support-email.after.ko.md` |
| 제안서 | `examples/proposal.before.ko.md` | `examples/proposal.after.ko.md` |
| 제품 문서 | `examples/docs.before.ko.md` | `examples/docs.after.ko.md` |
| 소셜 포스트 | `examples/social-post.before.ko.md` | `examples/social-post.after.ko.md` |

예시 출력은 정답 하나가 아닙니다. 같은 사실을 보존하면서도 더 나은 표현은 얼마든지 나올 수 있습니다.

## 저장소 구성

```text
.codex-plugin/plugin.json          Codex 플러그인 manifest
.claude-plugin/plugin.json         Claude Code 플러그인 manifest
.claude-plugin/marketplace.json    Claude Code marketplace 메타데이터
.agents/plugins/marketplace.json   Codex repo marketplace 메타데이터
plugins/humanizer-kr/              marketplace에서 설치되는 플러그인 패키지
skills/humanizer-kr/SKILL.md       공유 스킬 지침
skills/humanizer-kr/references/    한국어 근거 자료 정리
skills/humanizer-kr/scripts/       로컬 감사 도우미
examples/                          before/after 한국어 예시
scripts/sync_plugin_package.py     marketplace 패키지 사본 동기화
scripts/validate_package.py        릴리즈 검증 스크립트
```

## 릴리즈 검증

루트의 스킬, 문서, manifest를 수정한 뒤에는 marketplace용 패키지 사본을 동기화합니다.

```bash
python3 scripts/sync_plugin_package.py
```

그 다음 패키지 검증을 실행합니다.

```bash
python3 scripts/validate_package.py --release
```

테스트:

```bash
python3 -m unittest discover -s tests
```

Claude 플러그인 manifest 검증:

```bash
claude plugin validate plugins/humanizer-kr
```

Codex marketplace 설치 검증은 임시 `CODEX_HOME`을 사용하면 실제 사용자 설정을 건드리지 않고 확인할 수 있습니다.

```bash
CODEX_HOME=/tmp/humanizer-kr-codex-test codex plugin marketplace add hjongc/humanizer-kr --ref v0.1.4
CODEX_HOME=/tmp/humanizer-kr-codex-test codex plugin add humanizer-kr@humanizer-kr-marketplace
```

전체 체크리스트는 `RELEASE_CHECKLIST.md`에 있습니다.

## 참고 기준

- `skills/humanizer-kr/references/korean-source-rules.md`: 국립국어원 공공언어, 표준국어대사전, 우리말샘, 외래어 표기와 순화어 판단 기준
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing): AI 문체를 패턴 단위로 보는 접근 방식
- [blader/humanizer](https://github.com/blader/humanizer): README 구성과 패턴 문서화 방식의 참고 프로젝트

## 버전 히스토리

- **0.1.4** - `blader/humanizer` README 흐름을 참고해 한국어 README를 재구성했습니다. 한국어 AI 문체 패턴을 20개로 확장하고, 지원 이메일ㆍ제안서ㆍ제품 문서ㆍ소셜 포스트 예시를 추가했습니다.
- **0.1.3** - 한국어 README를 기본 문서로 전환했습니다.
- **0.1.2** - 한국어 README와 GitHub 공개 문서 흐름을 보강했습니다. Claude Code 설치 문서를 HTTPS marketplace 기준으로 정리했습니다.
- **0.1.1** - Claude Code marketplace metadata를 추가하고, installable plugin package에 root marketplace metadata가 섞이지 않도록 동기화를 보강했습니다.
- **0.1.0** - Codex/Claude 공용 스킬, 한국어 문체 지침, source-grounding reference, 예시, 감사 스크립트, 패키지 검증을 추가했습니다.

## 라이선스

MIT
