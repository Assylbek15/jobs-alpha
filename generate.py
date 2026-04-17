#!/usr/bin/env python3
import argparse
import importlib
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent
JOBS_DIR = REPO_ROOT / "jobs"


def to_xml(
    job: dict,
    source_tag: str,
    source_commit: str,
    release_version: str,
    generated_at: str,
) -> ET.Element:
    root = ET.Element("job", attrib={"name": job["name"]})

    meta = ET.SubElement(root, "meta")
    ET.SubElement(meta, "source_tag").text = source_tag
    ET.SubElement(meta, "source_commit").text = source_commit
    ET.SubElement(meta, "release_version").text = release_version
    ET.SubElement(meta, "generated_at").text = generated_at

    ET.SubElement(root, "schedule").text = job["schedule"]
    ET.SubElement(root, "timeout_seconds").text = str(job["timeout_seconds"])
    params_el = ET.SubElement(root, "parameters")
    for key, value in job.get("parameters", {}).items():
        ET.SubElement(params_el, "param", attrib={"name": key, "value": str(value)})

    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate job XML files.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--version", default=os.environ.get("VERSION", "unknown"))
    parser.add_argument("--source-commit", default="unknown")
    parser.add_argument("--release-version", default="unknown")
    args = parser.parse_args()

    source_tag = args.version
    source_commit = args.source_commit
    release_version = args.release_version
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(REPO_ROOT))

    count = 0
    for job_file in sorted(JOBS_DIR.glob("*.py")):
        if job_file.name.startswith("_"):
            continue

        module = importlib.import_module(f"jobs.{job_file.stem}")
        job = module.definition(source_tag)

        if job is None:
            print(f"  [skip] {job_file.stem} (not available in {source_tag})")
            continue

        root = to_xml(job, source_tag, source_commit, release_version, generated_at)
        ET.indent(root, space="  ")
        xml_str = ET.tostring(root, encoding="unicode") + "\n"

        out_path = output_dir / f"{job['name']}.xml"
        out_path.write_text(xml_str, encoding="utf-8")
        print(f"  [+] {job['name']}.xml")
        count += 1

    if count == 0:
        print(f"[WARN] No jobs generated for version {source_tag}.", file=sys.stderr)
    else:
        print(f"\nDone. {count} job(s) generated.")


if __name__ == "__main__":
    main()
