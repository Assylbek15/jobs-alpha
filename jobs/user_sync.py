def definition(version: str) -> dict:
    return {
        "name": "user_sync",
        "schedule": "0 2 * * *",
        "timeout_seconds": 3600,
        "parameters": {
            "batch_size": "1000",
            "source": "ldap",
            "target": "database",
        },
    }
