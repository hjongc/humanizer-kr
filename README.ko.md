# Humanizer KR

[English](README.md) | 한국어

Humanizer KR는 Codex와 Claude Code에서 사용할 수 있는 한국어 글쓰기 스킬입니다. AI가 쓴 것처럼 보이는 한국어 초안을 더 자연스럽고, 문맥에 맞고, 읽는 사람에게 맞는 문장으로 다듬습니다. 사실, 의도, 문단 흐름, 말투는 유지하고 표현만 고칩니다.

제품 카피, 공지문, 이메일, 문서, 제안서, 게시글처럼 한국어 문장이 어색하면 신뢰가 떨어지는 글에 맞춰 만들었습니다. 특히 번역투, 과한 홍보 문구, 명사화된 표현, 반복되는 수동 표현, 챗봇식 전개를 줄이는 데 초점을 둡니다.

## 할 수 있는 일

- 한국어 초안을 의미와 사실을 유지한 채 자연스럽게 다시 씁니다.
- `또한`, `이를 통해`, `혁신적인`, `최적화된`처럼 AI 글에서 자주 보이는 표현을 점검합니다.
- 제품 카피, 공지, 문서, 이메일, 게시글의 톤을 더 명확하고 담백하게 맞춥니다.
- 사용자가 제공한 한국어 샘플이 있으면 문장 길이, 어미, 리듬, 표현 습관을 참고해 맞춥니다.
- 국립국어원 등 신뢰할 수 있는 한국어 자료를 기준으로 외래어, 순화어, 표준 표현을 판단할 수 있게 돕습니다.

## 하지 않는 일

Humanizer KR는 AI 탐지기가 아닙니다. 감사 스크립트는 검토할 만한 표현 패턴을 알려줄 뿐, 어떤 글이 AI가 쓴 글인지 증명하지 않습니다.

표절을 숨기거나, 실제 인물이 쓴 것처럼 꾸미거나, 학업·채용·심사 절차를 우회하는 용도로 쓰면 안 됩니다. 사용자가 직접 작성했거나 고칠 권한이 있는 글을 더 명확하고 읽기 좋게 다듬는 용도에 맞춰져 있습니다.

## 설치: Codex

권장 방식은 GitHub marketplace를 추가한 뒤 플러그인을 설치하는 흐름입니다.

```bash
codex plugin marketplace add hjongc/humanizer-kr --ref v0.1.2
codex plugin add humanizer-kr@humanizer-kr-marketplace
```

설치 후 Codex를 재시작하면 `$humanizer-kr`로 사용할 수 있습니다.

```text
Use $humanizer-kr to make this Korean draft sound natural:
[고칠 한국어 초안]
```

개인용으로 단순히 스킬만 복사해서 쓰고 싶다면 아래 폴더를 Codex 스킬 디렉터리에 복사해도 됩니다.

```text
skills/humanizer-kr/ -> ~/.codex/skills/humanizer-kr/
```

## 설치: Claude Code

Claude Code에서는 HTTPS GitHub URL을 쓰는 방식을 권장합니다. `owner/repo` 형식은 환경에 따라 SSH clone을 시도할 수 있습니다.

```bash
claude plugin marketplace add https://github.com/hjongc/humanizer-kr.git
claude plugin install humanizer-kr@humanizer-kr-marketplace
```

설치 확인:

```bash
claude plugin list
```

Claude Code에서는 보통 아래처럼 네임스페이스를 붙여 호출합니다.

```text
/humanizer-kr:humanizer-kr
```

태그를 고정해서 쓰고 싶다면 로컬에 태그를 지정해 clone한 뒤 그 경로를 marketplace로 추가하세요.

```bash
git clone --branch v0.1.2 https://github.com/hjongc/humanizer-kr.git
claude plugin marketplace add ./humanizer-kr
claude plugin install humanizer-kr@humanizer-kr-marketplace
```

## 사용 예시

### 자연스럽게 다시 쓰기

```text
Use $humanizer-kr to make this Korean draft sound natural:
또한 본 솔루션은 혁신적인 AI 기술을 기반으로 사용자에게 최적화된 경험을 제공합니다.
```

### AI 티 나는 표현 리뷰하기

```text
Use $humanizer-kr to review this Korean copy for AI-like phrasing:
[검토할 한국어 문장]
```

### 내 문체에 맞추기

```text
Use $humanizer-kr. Match this sample voice:
[내가 쓴 한국어 샘플]

Rewrite this:
[고칠 초안]
```

## 로컬 감사 스크립트

스킬에는 간단한 패턴 감사 스크립트가 포함되어 있습니다. 이 스크립트는 문장을 고치지 않고, 검토할 표현만 표시합니다.

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

## 개발 및 검증

루트의 스킬·문서·manifest를 수정한 뒤에는 marketplace용 패키지 사본을 동기화합니다.

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
CODEX_HOME=/tmp/humanizer-kr-codex-test codex plugin marketplace add hjongc/humanizer-kr --ref v0.1.2
CODEX_HOME=/tmp/humanizer-kr-codex-test codex plugin add humanizer-kr@humanizer-kr-marketplace
```

## 저장소 구조

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

## 예시 파일

- `examples/product-copy.before.ko.md` -> `examples/product-copy.after.ko.md`
- `examples/public-notice.before.ko.md` -> `examples/public-notice.after.ko.md`

예시 출력은 참고용입니다. 같은 의미를 보존하면서도 더 나은 표현은 얼마든지 나올 수 있습니다.

## 한계

- 사실 검증 도구가 아닙니다. 사용자가 제공한 정보와 출처 안에서 표현을 다듬습니다.
- 감사 스크립트는 보수적인 패턴 검사입니다. 아무 것도 잡히지 않는다고 완성도 높은 한국어라는 뜻은 아닙니다.
- Claude Code 플러그인 동작은 설치된 Claude Code 버전에 따라 조금씩 다를 수 있습니다.

## 라이선스

MIT
