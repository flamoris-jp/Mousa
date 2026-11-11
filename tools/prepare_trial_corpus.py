"""Materialize only the three reviewed, hash-pinned Trial 001 MIDI sources.

Explicit CLI only: never called by a model. No credentials are used, no existing
output is replaced, and corpus bytes stay outside Git. --source-dir allows a
network-free recovery from the original experiment bundle.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "datasets/trial001-sources.json"
MAX_BYTES = 1024 * 1024


def obtain(work, source_dir):
    if source_dir is not None:
        path = Path(source_dir) / (work["work_id"] + ".mid")
        if path.is_symlink() or not path.is_file():
            raise ValueError("source must be a regular non-symlink MIDI file")
        with path.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
    else:
        url = work["midi_url"]
        parsed = urllib.parse.urlsplit(url)
        if (parsed.scheme != "https" or parsed.netloc != "www.mutopiaproject.org"
                or not parsed.path.startswith("/ftp/") or parsed.query or parsed.fragment):
            raise ValueError("unapproved source URL")
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                raise ValueError("source redirects require renewed review")
        opener = urllib.request.build_opener(NoRedirect())
        with opener.open(url, timeout=30) as response:
            data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or hashlib.sha256(data).hexdigest() != work["sha256"]:
        raise ValueError("source MIDI digest/size mismatch: " + work["work_id"])
    return data


def prepare(output, source_dir=None):
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("Choose a new corpus directory; no overwrite")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    if (catalog.get("schema_version") != "mousa.trial001.sources.v1" or
            [w["work_id"] for w in catalog["works"]] != ["mutopia-376", "mutopia-2247", "mutopia-2245"]):
        raise ValueError("trial source identity/order changed; preregister a new experiment")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".mousa-corpus-", dir=output.parent))
    try:
        works = []
        for entry in catalog["works"]:
            work = dict(entry)
            if work["license"] != "Public Domain" or not work.get("license_evidence"):
                raise ValueError("source not reviewed for this trial")
            if not re.fullmatch(r"[a-f0-9]{64}", work["sha256"]):
                raise ValueError("source hash format")
            data = obtain(work, source_dir)
            filename = work["work_id"] + ".mid"
            (staging / filename).write_bytes(data)
            # A transparent review record, not an HTML snapshot or legal opinion.
            evidence = (f"Work: {work['title']}\nComposer: {work['composer']}\n"
                        f"Inputter: {work['inputter']}\nEdition: {work['edition_source']}\n"
                        f"Source: {work['source_url']}\nCopyright field: Public Domain\n"
                        f"Reviewed: {work['license_reviewed_on']}\n"
                        f"Scope: {work['license_evidence']}\n").encode("utf-8")
            evidence_path = "source-pages/" + work["work_id"] + ".txt"
            (staging / "source-pages").mkdir(exist_ok=True)
            (staging / evidence_path).write_bytes(evidence)
            work.update(file=filename, status="usable", source_page_file=evidence_path,
                        source_page_sha256=hashlib.sha256(evidence).hexdigest(),
                        evidence_kind="review_record_not_html_snapshot")
            works.append(work)
        manifest = {"schema_version": "music.corpus.v1", "works": works,
                    "purpose": "Reproduce existing train/dev/test diagnostic, not aesthetic selection",
                    "catalog_sha256": hashlib.sha256(CATALOG.read_bytes()).hexdigest()}
        (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # Exclusive reservation; never replace an existing corpus directory.
        output.mkdir()
        for item in staging.iterdir():
            shutil.move(str(item), output / item.name)
        return output / "manifest.json"
    finally:
        shutil.rmtree(staging)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path)
    args = parser.parse_args()
    print(prepare(args.output, args.source_dir))
