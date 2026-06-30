#!/usr/bin/env python3
"""Validate the Humanizer KR package before release."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "https://github.com/OWNER/humanizer-kr"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON in {path}: {exc}") from exc


def repository_url(manifest: dict) -> str:
    repository = manifest.get("repository", "")
    if isinstance(repository, dict):
        return str(repository.get("url", ""))
    return str(repository)


def validate_manifest(path: Path, expected_skills: str, *, release: bool) -> None:
    manifest = load_json(path)
    for key in ("name", "version", "description", "license"):
        require(bool(manifest.get(key)), f"{path} missing {key}")
    require(manifest.get("skills") == expected_skills, f"{path} skills must be {expected_skills!r}")
    repo_url = repository_url(manifest)
    require(bool(repo_url), f"{path} repository URL is empty")
    if release:
        require(repo_url != PLACEHOLDER, f"{path} still uses placeholder repository URL")


def validate_skill() -> None:
    skill_path = ROOT / "skills" / "humanizer-kr" / "SKILL.md"
    require(skill_path.exists(), "skills/humanizer-kr/SKILL.md is missing")
    text = skill_path.read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    require(frontmatter is not None, "SKILL.md missing YAML frontmatter")
    header = frontmatter.group(1)
    require(re.search(r"^name:\s*humanizer-kr\s*$", header, re.MULTILINE) is not None, "SKILL.md frontmatter name must be humanizer-kr")
    require(re.search(r"^description:\s*.+", header, re.MULTILINE) is not None, "SKILL.md frontmatter description is missing")
    require("AI-generated" in text or "AI-writing" in text, "SKILL.md should define AI-writing scope")
    require("does not prove a text is AI-generated" in text, "SKILL.md must avoid AI-detector claims")
    require("Never add facts" in text, "SKILL.md must preserve facts")


def validate_references() -> None:
    refs = ROOT / "skills" / "humanizer-kr" / "references" / "korean-source-rules.md"
    require(refs.exists(), "source-grounding reference is missing")
    scripts = ROOT / "skills" / "humanizer-kr" / "scripts" / "audit_korean_text.py"
    require(scripts.exists(), "audit script is missing")
    require(scripts.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3"), "audit script should be executable Python")


def validate_marketplace() -> None:
    path = ROOT / ".agents" / "plugins" / "marketplace.json"
    require(path.exists(), ".agents/plugins/marketplace.json is missing")
    marketplace = load_json(path)
    require(bool(marketplace.get("name")), "marketplace missing name")
    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list) and plugins, "marketplace plugins must be a non-empty list")
    names = {plugin.get("name") for plugin in plugins if isinstance(plugin, dict)}
    require("humanizer-kr" in names, "marketplace must include humanizer-kr")
    for plugin in plugins:
        require(bool(plugin.get("category")), "marketplace plugin missing category")
        policy = plugin.get("policy", {})
        installation = policy.get("installation")
        authentication = policy.get("authentication")
        require(installation in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}, "marketplace plugin has invalid policy.installation")
        require(authentication in {"ON_INSTALL", "ON_USE"}, "marketplace plugin has invalid policy.authentication")
        source = plugin.get("source")
        if isinstance(source, dict):
            require(source.get("source") == "local", "marketplace source.source must be local for repo-local distribution")
            source_path = source.get("path")
            require(isinstance(source_path, str) and source_path.startswith("./"), "marketplace source.path must start with ./")
        else:
            require(isinstance(source, str) and source.startswith("./"), "marketplace source must be a relative ./ path")


def validate_claude_marketplace() -> None:
    path = ROOT / ".claude-plugin" / "marketplace.json"
    require(path.exists(), ".claude-plugin/marketplace.json is missing")
    marketplace = load_json(path)
    require(marketplace.get("$schema") == "https://anthropic.com/claude-code/marketplace.schema.json", "Claude marketplace schema URL is missing or invalid")
    require(marketplace.get("name") == "humanizer-kr-marketplace", "Claude marketplace name must be humanizer-kr-marketplace")
    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list) and plugins, "Claude marketplace plugins must be a non-empty list")
    plugin = plugins[0]
    require(plugin.get("name") == "humanizer-kr", "Claude marketplace plugin name must be humanizer-kr")
    require(plugin.get("source") == "./plugins/humanizer-kr", "Claude marketplace source must point to ./plugins/humanizer-kr")
    require(bool(plugin.get("description")), "Claude marketplace plugin description is missing")
    require(bool(plugin.get("category")), "Claude marketplace plugin category is missing")


def validate_packaged_plugin_copy() -> None:
    package_root = ROOT / "plugins" / "humanizer-kr"
    require(package_root.exists(), "plugins/humanizer-kr marketplace package is missing")
    required_paths = [
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        "skills/humanizer-kr/SKILL.md",
        "skills/humanizer-kr/references/korean-source-rules.md",
        "skills/humanizer-kr/scripts/audit_korean_text.py",
        "LICENSE",
        "README.md",
        "README.en.md",
    ]
    require(not (package_root / ".claude-plugin" / "marketplace.json").exists(), "packaged plugin must not contain root Claude marketplace metadata")
    for rel in required_paths:
        source = ROOT / rel
        packaged = package_root / rel
        require(packaged.exists(), f"packaged plugin missing {rel}")
        require(
            source.read_text(encoding="utf-8") == packaged.read_text(encoding="utf-8"),
            f"packaged plugin copy is stale for {rel}",
        )


def validate_examples() -> None:
    examples = ROOT / "examples"
    before_files = sorted(examples.glob("*.before.ko.md"))
    after_files = sorted(examples.glob("*.after.ko.md"))
    require(before_files, "at least one before example is required")
    require(after_files, "at least one after example is required")
    for before in before_files:
        after = before.with_name(before.name.replace(".before.", ".after."))
        require(after.exists(), f"missing paired after example for {before.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Humanizer KR package metadata and release fixtures.")
    parser.add_argument("--release", action="store_true", help="Fail if publish-time placeholders remain.")
    args = parser.parse_args()
    validate_manifest(ROOT / ".codex-plugin" / "plugin.json", "./skills/", release=args.release)
    validate_manifest(ROOT / ".claude-plugin" / "plugin.json", "./skills/", release=args.release)
    validate_skill()
    validate_references()
    validate_marketplace()
    validate_claude_marketplace()
    validate_packaged_plugin_copy()
    validate_examples()
    print("Humanizer KR package validation passed.")


if __name__ == "__main__":
    main()
