def _at_least(version: str, minimum: str) -> bool:
    def parts(v: str) -> tuple:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    return parts(version) >= parts(minimum)


def definition(version: str) -> dict:
    params = {
        "format": "csv",
        "destination": "s3://reports-bucket/exports",
        "compression": "gzip",
    }
    if _at_least(version, "v1.1.0"):
        params["parallel_uploads"] = "true"

    return {
        "name": "data_export",
        "schedule": "0 6 * * 1",
        "timeout_seconds": 7200,
        "parameters": params,
    }
