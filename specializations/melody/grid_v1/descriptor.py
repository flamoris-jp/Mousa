"""Mousa migration of the recovered MIDI trial; external Maidionis Core is unchanged.

This is an offline next-token research task, not a musical-quality critic.
"""
from pathlib import Path
import os
import subprocess

from maidionis_education.contracts import RegistryBuilder, canonical, digest
from maidionis_education.datasets import DatasetHooks

HERE = Path(__file__).resolve().parent
UPSTREAM = "a987eeeea11e3971d3b9708bfff6b3545cdb601f"
if not os.environ.get("MOUSA_MAIDIONIS_ROOT"):
    raise RuntimeError("Set MOUSA_MAIDIONIS_ROOT to the pinned external Maidionis checkout")
ROOT = Path(os.environ["MOUSA_MAIDIONIS_ROOT"]).resolve()
head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, timeout=10).strip()
if head != UPSTREAM:
    raise RuntimeError("Maidionis checkout does not match the recorded commit")
subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "HEAD"], check=True, timeout=10)
PREFIX = "research.music-next-token."
IDENTITY = dict(specialization_id="research.music-next-token", specialization_version="1",
                task_id="research.music-next-token", task_version="1")
SPEC = ("Music Next Token v1: predict one sixteenth-grid token from the previous eight tokens "
        "and position modulo 16. Token 0 is REST, 1 is HOLD, and 2..26 are MIDI pitches 60..84. "
        "Work SHA-256 is provenance only and is excluded from model features. "
        "Offline research; no musical-quality or production claim.\n").encode()


def core_build_digest(root=ROOT):
    paths = ["CMakeLists.txt", "tests/tinybeat.py", "tests/fixture_data.py",
             "tests/tinybeat_composition.cpp", "tests/tinybeat_composition.h"]
    for pattern in ("include/maidionis/*.h", "src/**/*.cpp", "contracts/*.schema.json",
                    "education/python/src/maidionis_education/*.py"):
        paths.extend(p.relative_to(root).as_posix() for p in root.glob(pattern))
    raw = b"maidionis-code-build-v1\n" + b"".join(
        (p + "\n" + digest((root / p).read_bytes()) + "\n").encode() for p in sorted(paths))
    return digest(raw)


def specialty_source_digest(here=HERE):
    paths = [*here.glob("*.py"), *here.glob("native/*.cpp"), *here.glob("native/*.h"),
             here / "native/CMakeLists.txt"]
    names = sorted({p.relative_to(here).as_posix() for p in paths if p.is_file()})
    return digest(b"maidionis-music-sources-v1\n" + b"".join(
        (p + "\n" + digest((here / p).read_bytes()) + "\n").encode() for p in names))


def build_digest():
    return digest(("maidionis-music-build-v1\n" + core_build_digest() + "\n" +
                   specialty_source_digest() + "\n").encode())


def object_schema(fields):
    return dict(type="object", properties=fields, required=list(fields), additionalProperties=False)


INPUT = object_schema(dict(
    work_sha256=dict(type="string", pattern="^[a-f0-9]{64}$"),
    tokens=dict(type="array", minItems=8, maxItems=8,
                items=dict(type="integer", minimum=0, maximum=26)),
    position=dict(type="integer", minimum=0, maximum=15)))
OUTPUT = object_schema(dict(token=dict(type="integer", minimum=0, maximum=26)))
SCHEMAS = {"input": INPUT, "target": OUTPUT, "output": OUTPUT}
CONFIGS = {
    "input_codec": {"context_steps": 8, "classes": 27, "positions": 16,
                    "encoding": "onehot-context-position-v1", "features": 232},
    "output_codec": {"decode": "argmax-first-v1", "classes": 27},
    "architecture": {"kind": "dense", "input_width": 232, "hidden_width": 64,
                     "output_width": 27, "dropout_milli": 0},
    "head": {"outputs": 27},
    "objective": {"kind": "categorical", "reduction": "mean", "eligibility": "all-rows"},
    "numerical_compatibility": {"profile": "linux.cpu.fp32.serial.v1", "libtorch": "2.5.1", "archive": 1},
}


def ref(name):
    return dict(id=PREFIX + name, version="1", sha256=digest(canonical(SCHEMAS[name])))


def config_ref(name, config):
    return dict(id=PREFIX + name, version="1", config_digest=digest(canonical(config)))


DESCRIPTOR = dict(
    schema_version="maidionis.specialization.v1", **IDENTITY,
    input_schema=ref("input"), target_schema=ref("target"), output_schema=ref("output"),
    diagnostics_schema=None, semantic_spec=dict(path="semantic.txt", sha256=digest(SPEC)),
    heads=[config_ref("head", CONFIGS["head"])],
    **{k: config_ref(k, v) for k, v in CONFIGS.items() if k != "head"})


def registry():
    b = RegistryBuilder(build_digest())
    for key, schema in SCHEMAS.items():
        b.add_schema(ref(key), schema)
    for key, value in CONFIGS.items():
        b.add_operation(config_ref(key, value), value, lambda config: None)
    return b.freeze(DESCRIPTOR)


def component_files():
    return {"descriptor.json": canonical(DESCRIPTOR), "semantic.txt": SPEC,
            **{k + ".schema.json": canonical(v) for k, v in SCHEMAS.items()},
            **{k + ".config.json": canonical(v) for k, v in CONFIGS.items()}}


def dataset_profiles(sources):
    source_digest = digest(canonical(sources))
    profiles = {
        "group": config_ref("group", {"projection": "work-sha256-v1"}),
        "dedup": config_ref("dedup", {"projection": "work-window-v1"}),
        "hook": config_ref("dataset-hooks", {"implementation": "music-sources-v1", "build_digest": build_digest()}),
        "verify": config_ref("source-verifier", {"verification": "source-window-target-v1", "sources_digest": source_digest}),
        "generator": config_ref("generator", {"pipeline": "midi-monophonic-grid-v1", "context_steps": 8,
                                               "classes": 27, "sources_digest": source_digest}),
    }
    return profiles


def dataset_hooks(sources):
    works = {w["work_sha256"]: w for w in sources["works"]}
    if len(works) != len(sources["works"]):
        raise ValueError("duplicate source work")
    profiles = dataset_profiles(sources)

    def verify(row, proof):
        try:
            source = works[row["input"]["work_sha256"]]
            prefix, sha, index_text = row["sample_id"].split(":")
            index = int(index_text)
            return (prefix == "midi" and str(index) == index_text and sha == source["work_sha256"]
                    and 8 <= index < len(source["tokens"])
                    and row["input"]["tokens"] == source["tokens"][index - 8:index]
                    and row["input"]["position"] == index % 16
                    and row["target"] == {"token": source["tokens"][index]}
                    and row["split"] == source["split"] and row["supersedes"] is None
                    and proof["ancestry"] == [sha] and proof["outcome"] == "verified")
        except (KeyError, ValueError, IndexError):
            return False

    return DatasetHooks(
        profiles["hook"], profiles["group"], profiles["dedup"], profiles["verify"],
        lambda x: [{"work_sha256": x["work_sha256"]}],
        lambda x: x, verify, split_algorithm="research.music.by-work.v1",
        assign_split=lambda x, fingerprint, seed: works[x["work_sha256"]]["split"])
