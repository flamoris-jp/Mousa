"""Offline research manifest checks; never grants legal rights or downloads data.

This preflight is independent of the experimental MIDI frontend in PR #6.
It checks explicit review records and split leakage, not musical quality.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
import re
from urllib.parse import urlsplit

SCHEMA = "mousa.research-intake.v1"
HEX = re.compile(r"[0-9a-f]{64}\Z")
RIGHTS = ("composition", "arrangement", "midi_encoding")


def validate_manifest(manifest: dict, root: Path) -> dict:
    """Validate the full catalogue before any eligible subset is selected.

    Pending/excluded records remain in the manifest but cannot have a split.
    Group IDs are reviewer assertions: callers must separately run approximate
    duplicate detection and preserve its method/results. This is not a detector.
    """
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA:
        raise ValueError("unsupported manifest schema")
    works = manifest.get("works")
    if not isinstance(works, list) or len(works) > 10000:
        raise ValueError("works must be a bounded list")
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")
    ids, groups, hashes = set(), {}, {}
    counts = {key: 0 for key in ("train", "dev", "test", "quarantined")}
    for work in works:
        if not isinstance(work, dict):
            raise ValueError("work must be an object")
        for key in ("work_id", "title", "author", "source_url", "license", "terms", "acquired_at", "sha256", "family_id", "duplicate_group"):
            if not isinstance(work.get(key), str) or not work[key].strip():
                raise ValueError("missing text field: " + key)
        if work["work_id"] in ids:
            raise ValueError("duplicate work_id")
        ids.add(work["work_id"])
        if urlsplit(work["source_url"]).scheme != "https" or not urlsplit(work["source_url"]).netloc:
            raise ValueError("source must be an HTTPS URL")
        if not HEX.fullmatch(work["sha256"]):
            raise ValueError("invalid source hash")
        when = datetime.fromisoformat(work["acquired_at"].replace("Z", "+00:00"))
        if when.tzinfo is None:
            raise ValueError("acquired_at must have timezone")
        state = work.get("review_state")
        if state not in ("pending", "approved", "excluded"):
            raise ValueError("invalid review state")
        split = work.get("split")
        if state != "approved":
            if split is not None or work.get("training_allowed") is not False:
                raise ValueError("unapproved work must be quarantined")
            counts["quarantined"] += 1
            continue
        if work.get("training_allowed") is not True or split not in ("train", "dev", "test"):
            raise ValueError("approved work needs explicit training permission and split")
        rights = work.get("rights")
        if not isinstance(rights, dict) or set(rights) != set(RIGHTS):
            raise ValueError("review composition, arrangement and MIDI separately")
        for right in RIGHTS:
            record = rights[right]
            if not isinstance(record, dict) or record.get("training_allowed") is not True:
                raise ValueError("unapproved rights: " + right)
            if not all(isinstance(record.get(k), str) and record[k].strip() for k in ("basis", "evidence_url", "reviewed_on")):
                raise ValueError("missing rights evidence")
            if urlsplit(record["evidence_url"]).scheme != "https" or not urlsplit(record["evidence_url"]).netloc:
                raise ValueError("rights evidence must be an HTTPS URL")
            datetime.strptime(record["reviewed_on"], "%Y-%m-%d")
        # Reviewed AudioAnalyzer candidates are not interchangeable with MIDI.
        if work.get("source_kind") != "midi":
            raise ValueError("this preflight accepts reviewed MIDI only")
        relative = work.get("file")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("unsafe source path")
        path = root
        for part in Path(relative).parts:
            path = path / part
            if path.is_symlink():
                raise ValueError("symlink source forbidden")
        path = path.resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size > 1048576:
            raise ValueError("source is not a bounded regular file")
        data = path.read_bytes()
        if len(data) > 1048576 or hashlib.sha256(data).hexdigest() != work["sha256"]:
            raise ValueError("source hash mismatch")
        # MIDI header only: the real parser must still reject malformed events.
        if not data.startswith(b"MThd"):
            raise ValueError("not a MIDI header")
        for key in ("family_id", "duplicate_group"):
            group = (key, work[key])
            if group in groups and groups[group] != split:
                raise ValueError("family/near-duplicate split leakage")
            groups[group] = split
        if work["sha256"] in hashes:
            raise ValueError("duplicate source bytes")
        hashes[work["sha256"]] = split
        counts[split] += 1
    return {"counts": counts, "scope": "preflight only; no legal or musical judgement"}
