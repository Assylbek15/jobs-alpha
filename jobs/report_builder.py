def _at_least(version: str, minimum: str) -> bool:
    def parts(v: str) -> tuple:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    return parts(version) >= parts(minimum)


def definition(version: str) -> dict | None:
    if not _at_least(version, "v1.1.0"):
        return None

    return {
        "name": "report_builder",
        "schedule": "0 8 * * 1-5",
        "timeout_seconds": 1800,
        "parameters": {
            "template": "weekly_summary",
            "recipients": "ops-team@company.com",
        },
    }
