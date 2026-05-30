"""Behavior tests for the Skill Body Parity module (skill_parity.py).

Owns frontmatter stripping and the canonical-vs-distributed-copies body
comparison, sourcing artifact paths from the Distribution Inventory.
"""

from __future__ import annotations

from pathlib import Path

from codeforerunner import distribution as dist
from codeforerunner import skill_parity as sp


# --- frontmatter -----------------------------------------------------------


def test_body_of_strips_frontmatter_and_trims():
    text = "---\nname: x\nversion: 1\n---\n\nthe body\n"
    assert sp.body_of(text) == "the body"


def test_body_of_without_frontmatter_returns_trimmed_text():
    assert sp.body_of("  plain text\n") == "plain text"


def test_body_of_normalizes_crlf():
    assert sp.body_of("---\r\na: 1\r\n---\r\nbody\r\n") == "body"


def test_split_frontmatter_returns_block_and_body():
    block, body = sp.split_frontmatter("---\nname: x\n---\nbody\n")
    assert block == "---\nname: x\n---\n"
    assert body == "body"


def test_split_frontmatter_no_frontmatter_has_empty_block():
    block, body = sp.split_frontmatter("just body")
    assert block == ""
    assert body == "just body"


# --- parity ----------------------------------------------------------------


def _write_checkout(root: Path, *, canonical: str, copies: dict[Path, str]) -> None:
    cpath = root / dist.CANONICAL_SKILL_REL
    cpath.parent.mkdir(parents=True, exist_ok=True)
    cpath.write_text(canonical, encoding="utf-8")
    for rel, text in copies.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def test_parity_ok_when_bodies_match(tmp_path):
    body = "---\na: 1\n---\nshared body\n"
    copies = {rel: body for rel in dist.DISTRIBUTED_SKILL_COPIES_REL}
    _write_checkout(tmp_path, canonical=body, copies=copies)

    result = sp.check_skill_body_parity(tmp_path)
    assert result.ok
    assert result.checked == len(dist.DISTRIBUTED_SKILL_COPIES_REL)
    assert not result.drifted_copies and not result.missing_copies
    assert not result.missing_canonical


def test_parity_detects_body_drift(tmp_path):
    canonical = "---\na: 1\n---\ncanonical body\n"
    rels = list(dist.DISTRIBUTED_SKILL_COPIES_REL)
    copies = {rels[0]: canonical, rels[1]: "---\nb: 2\n---\nDRIFTED body\n"}
    _write_checkout(tmp_path, canonical=canonical, copies=copies)

    result = sp.check_skill_body_parity(tmp_path)
    assert not result.ok
    assert rels[1] in result.drifted_copies
    assert rels[0] not in result.drifted_copies


def test_parity_reports_missing_copy(tmp_path):
    canonical = "body\n"
    rels = list(dist.DISTRIBUTED_SKILL_COPIES_REL)
    _write_checkout(tmp_path, canonical=canonical, copies={rels[0]: canonical})  # rels[1] absent

    result = sp.check_skill_body_parity(tmp_path)
    assert not result.ok
    assert rels[1] in result.missing_copies


def test_parity_reports_missing_canonical(tmp_path):
    copies = {rel: "body\n" for rel in dist.DISTRIBUTED_SKILL_COPIES_REL}
    for rel, text in copies.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    # canonical not written

    result = sp.check_skill_body_parity(tmp_path)
    assert not result.ok
    assert result.missing_canonical
