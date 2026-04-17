#!/usr/bin/env python3
import argparse
import importlib
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).parent
JOBS_DIR = REPO_ROOT / "jobs"


def to_xml(job: dict, version: str) -> ET.Element:
    root = ET.Element("job", attrib={"name": job["name"], "version": version})
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
    args = parser.parse_args()

    version = args.version
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(REPO_ROOT))

    count = 0
    for job_file in sorted(JOBS_DIR.glob("*.py")):
        if job_file.name.startswith("_"):
            continue

        module = importlib.import_module(f"jobs.{job_file.stem}")
        job = module.definition(version)

        if job is None:
            print(f"  [skip] {job_file.stem} (not available in {version})")
            continue

        root = to_xml(job, version)
        ET.indent(root, space="  ")
        xml_str = ET.tostring(root, encoding="unicode") + "\n"

        out_path = output_dir / f"{job['name']}.xml"
        out_path.write_text(xml_str, encoding="utf-8")
        print(f"  [+] {job['name']}.xml")
        count += 1

    if count == 0:
        print(f"[WARN] No jobs generated for version {version}.", file=sys.stderr)
    else:
        print(f"\nDone. {count} job(s) generated.")


if __name__ == "__main__":
    main()
