#!/usr/bin/env python3
"""Record explicit voice feedback and safely undo the latest profile change."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import uuid


HEADING = "## Explicit User Preferences"
FIELDS = {"expected_profile_sha256", "preference", "replace", "before", "after", "reason", "scope", "choice"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_directory(project: Path, home: Path, explicit: Path | None = None) -> Path:
    candidates = [explicit] if explicit is not None else [project / ".humanizer-kr", home / ".humanizer-kr"]
    for candidate in candidates:
        if (candidate / "voice.md").is_file():
            return candidate
    raise ValueError("No voice.md found; run Analyze first or select its directory with --directory")


def valid_hex(value, size: int) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{" + str(size) + "}", value) is not None


def atomic_write(path: Path, data: bytes) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".feedback-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


@contextmanager
def locked(directory: Path):
    path = directory / ".feedback.lock"
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Feedback is already being updated, or an interrupted run left .feedback.lock; inspect before removing it") from None
    try:
        os.write(descriptor, str(os.getpid()).encode())
        os.close(descriptor)
        yield
    finally:
        path.unlink()


def history(directory: Path) -> list[dict]:
    path = directory / "analysis" / "voice-feedback.jsonl"
    if not path.exists():
        return []
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for row in records:
        if (not isinstance(row, dict) or row.get("operation") not in {"record", "undo"}
                or not valid_hex(row.get("id"), 32)
                or not valid_hex(row.get("profile_before_sha256"), 64)
                or not valid_hex(row.get("profile_after_sha256"), 64)
                or (row["operation"] == "record" and not isinstance(row.get("profile_changed"), bool))
                or (row["operation"] == "undo" and not valid_hex(row.get("target_id"), 32))):
            raise ValueError("Invalid feedback history; inspect it before updating")
    return records


def latest_change(records: list[dict]) -> dict | None:
    undone = {row["target_id"] for row in records if row["operation"] == "undo"}
    return next((row for row in reversed(records) if row["operation"] == "record"
                 and row.get("profile_changed") and row["id"] not in undone), None)


def append_record(directory: Path, record: dict) -> None:
    path = directory / "analysis" / "voice-feedback.jsonl"
    path.parent.mkdir(exist_ok=True, mode=0o700)
    previous = path.read_bytes() if path.exists() else b""
    separator = b"\n" if previous and not previous.endswith(b"\n") else b""
    atomic_write(path, previous + separator + json.dumps(record, ensure_ascii=False).encode() + b"\n")


def update_preferences(text: str, preference: str, replacements: list[str]) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    pattern = r"^" + re.escape(HEADING) + r"[ \t]*(?:\r?\n|$)"
    matches = list(re.finditer(pattern, text, re.M))
    if len(matches) > 1:
        raise ValueError("Multiple explicit preferences sections; resolve the ambiguity first")
    if not matches:
        if replacements:
            raise ValueError("Cannot replace preferences: the explicit preferences section is missing")
        text = text.rstrip() + newline * 2 + HEADING + newline
        matches = list(re.finditer(pattern, text, re.M))
    start = matches[0].end()
    next_heading = re.search(r"^#{1,2} ", text[start:], re.M)
    end = start + next_heading.start() if next_heading else len(text)
    section = text[start:end]
    lines = section.splitlines()
    if any(not line.startswith("- ") or lines.count(line) != 1 for line in replacements):
        raise ValueError("Each replace entry must exactly match one bullet in the explicit preferences section")
    lines = [line for line in lines if line not in replacements]
    bullet = "- User preference: " + " ".join(preference.split())
    if bullet not in lines:
        lines.append(bullet)
    prefix = text[:start]
    if not prefix.endswith("\n"):
        prefix += newline
    return prefix + newline + newline.join(lines).strip() + newline * 2 + text[end:]


def validate_payload(payload: dict) -> None:
    if not isinstance(payload, dict) or set(payload) - FIELDS:
        raise ValueError("Feedback must be an object containing only supported fields")
    for key in FIELDS - {"replace"}:
        if key in payload and (not isinstance(payload[key], str) or (key not in {"before", "after"} and not payload[key].strip())):
            raise ValueError(f"{key} must be a nonempty string")
    replacements = payload.get("replace", [])
    if not isinstance(replacements, list) or any(not isinstance(item, str) for item in replacements) or len(set(replacements)) != len(replacements):
        raise ValueError("replace must be a list of unique exact preference bullets")
    if replacements and "preference" not in payload:
        raise ValueError("replace requires an explicit preference")
    if ("before" in payload) != ("after" in payload):
        raise ValueError("A correction requires both before and after")
    if "before" in payload and not (payload["before"].strip() or payload["after"].strip()):
        raise ValueError("A correction must contain text before or after")
    if "choice" in payload and payload["choice"] not in {"A", "B", "tie", "neither"}:
        raise ValueError("choice must be A, B, tie, or neither")
    if not any(key in payload for key in ("preference", "before", "choice")):
        raise ValueError("Provide an explicit preference, a correction, or a comparison choice")
    if not valid_hex(payload.get("expected_profile_sha256"), 64):
        raise ValueError("expected_profile_sha256 must be the hash returned by show")


def record_feedback(directory: Path, payload: dict) -> dict:
    validate_payload(payload)
    with locked(directory):
        history(directory)
        profile = directory / "voice.md"
        before = profile.read_bytes()
        if digest(before) != payload["expected_profile_sha256"]:
            raise ValueError("Profile changed since show; read it again before recording feedback")
        after = update_preferences(before.decode("utf-8"), payload["preference"], payload.get("replace", [])).encode() if "preference" in payload else before
        record = {"id": uuid.uuid4().hex, "operation": "record", "created_at": datetime.now(timezone.utc).isoformat(),
                  "feedback": {key: value for key, value in payload.items() if key != "expected_profile_sha256"},
                  "profile_before_sha256": digest(before), "profile_after_sha256": digest(after), "profile_changed": before != after}
        backup = directory / "analysis" / "voice-feedback-backups" / (record["id"] + ".md")
        if before != after:
            backup.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            atomic_write(backup, before)
            atomic_write(profile, after)
        try:
            append_record(directory, record)
        except Exception:
            # Restore only our own write, preserving a newer manual edit if one appeared.
            if before != after and profile.read_bytes() == after:
                atomic_write(profile, before)
            raise
        return record


def undo(directory: Path) -> dict:
    with locked(directory):
        target = latest_change(history(directory))
        if target is None:
            raise ValueError("No active feedback profile change to undo")
        profile = directory / "voice.md"
        current = profile.read_bytes()
        if digest(current) != target["profile_after_sha256"]:
            raise ValueError("Profile changed after this feedback; refusing to overwrite newer edits")
        backup = directory / "analysis" / "voice-feedback-backups" / (target["id"] + ".md")
        previous = backup.read_bytes()
        if digest(previous) != target["profile_before_sha256"]:
            raise ValueError("Backup hash mismatch; refusing to restore")
        record = {"id": uuid.uuid4().hex, "operation": "undo", "created_at": datetime.now(timezone.utc).isoformat(),
                  "target_id": target["id"], "profile_before_sha256": digest(current), "profile_after_sha256": digest(previous)}
        atomic_write(profile, previous)
        try:
            append_record(directory, record)
        except Exception:
            if profile.read_bytes() == previous:
                atomic_write(profile, current)
            raise
        return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("show", "record", "undo"))
    parser.add_argument("--directory", type=Path, help="explicit directory containing voice.md")
    parser.add_argument("--input", type=Path, help="JSON feedback payload for record")
    args = parser.parse_args()
    try:
        directory = resolve_directory(Path.cwd(), Path.home(), args.directory.expanduser() if args.directory else None)
        if args.action == "show":
            data = (directory / "voice.md").read_bytes()
            result = {"directory": str(directory), "profile_sha256": digest(data), "profile": data.decode("utf-8"),
                      "latest_change": latest_change(history(directory))}
        elif args.action == "record":
            if args.input is None:
                raise ValueError("record requires --input PATH")
            result = record_feedback(directory, json.loads(args.input.read_text(encoding="utf-8")))
        else:
            result = undo(directory)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
