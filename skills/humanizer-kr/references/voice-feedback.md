# Voice Feedback

Use for `/humanizer-kr:feedback` or an explicit request to save a lasting preference, record a correction, or undo a feedback change. This workflow needs an existing `voice.md`. It never writes raw writing samples or rebuilds inferred observations.

## Resolve and Inspect

Run the bundled helper from the skill directory (resolve the actual absolute path):

```bash
python3 "<skill-directory>/scripts/voice_feedback.py" show
```

It selects the current project's `.humanizer-kr/voice.md`, then the personal `~/.humanizer-kr/voice.md`. Use `--directory "<voice-directory>"` only for an explicit storage selection. Keep the returned directory for subsequent calls so the same profile is updated. If no profile exists, explain that Analyze must create one first; do not silently invent one.

`show` returns the profile and its `profile_sha256`. Read existing explicit preferences and identify any that directly conflict with the new explicit instruction. An explicit preference overrides inferred sample traits, including historical sentence-length statistics. Preserve unrelated preferences and every other profile section.

## Record

Use the available file-writing tool (`Write` or `apply_patch`) to create a uniquely named UTF-8 JSON file inside the resolved voice directory, for example `.feedback-input-<unique-id>.json`, with the returned hash and the user's feedback. Keep this private input with the voice data rather than leaving it in the working directory. Do not create it with a shell heredoc or embed user text in a shell command. Then run the helper as a separate Python command, without shell variables or chained setup commands:

```bash
python3 "<skill-directory>/scripts/voice_feedback.py" record --directory "<voice-directory>" --input "<voice-directory>/.feedback-input-<unique-id>.json"
```

The accepted fields are:

- `expected_profile_sha256`: required hash from `show`; stale input is rejected.
- `preference`: the user's explicit lasting style preference. Keep the meaning and scope; do not infer it from a winning text, a single correction, or its topic. Omit this field when there is no explicit rule.
- `replace`: optional list of exact old bullet lines from `## Explicit User Preferences`, only when the current instruction supersedes those specific preferences. Do not replace inferred observations or unrelated preferences.
- `before` and `after`: both required for a correction; preserve the text exactly. An empty `after` records a deletion. A correction alone never changes the profile.
- `reason`: the user's supplied reason, when available. Omit it instead of guessing; ask briefly if a reason is needed to understand an intended lasting rule.
- `scope`: supplied genre or scope, when available. Include scope in the preference wording itself when it limits a saved rule.
- `choice`: optional `A`, `B`, `tie`, or `neither`. For comparison choices, use `scope` to identify the comparison. Do not derive a preference from the choice alone.

Example payload for a direct preference:

```json
{
  "expected_profile_sha256": "<hash returned by show>",
  "preference": "Prefer concise sentences and meaningful connectors."
}
```

The helper appends a clearly labeled user preference inside the explicit section. It saves correction/reason/choice metadata under `analysis/voice-feedback.jsonl`; it does not treat those examples as general rules. Changes keep a private backup in `analysis/voice-feedback-backups/`. JSON must be data: never interpolate user text into a shell command. Report success only after the helper succeeds and `show` confirms the saved state. Show the added/replaced preferences and saved location in ordinary language.

## Undo

For an explicit undo request:

```bash
python3 "<skill-directory>/scripts/voice_feedback.py" undo --directory "<voice-directory>"
```

This restores the latest active profile change made by this helper; correction-only and choice-only records remain intact. Repeated undo walks backward through active changes. It does not revert an unrelated Analyze operation or an ad-hoc manual edit. A changed current-profile hash or damaged backup makes undo fail visibly instead of overwriting newer edits. Do not force a restore after that refusal.

The helper serializes its own writers with `.feedback.lock`. An interrupted process can leave that lock and backups; inspect the recorded process ID before removing a stale lock. Do not automatically remove a lock or discard a backup. Ordinary manual editors do not participate in this lock, so always inspect current state after a conflict.
