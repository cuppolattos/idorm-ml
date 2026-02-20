from pathlib import Path

def get_next_version(region_path: Path, bump="patch"):
    """
    bump: 'patch', 'minor', 'major'
    """

    if not region_path.exists():
        return "v1.0.0"

    versions = []

    for folder in region_path.iterdir():
        if folder.is_dir() and folder.name.startswith("v"):
            versions.append(folder.name.replace("v", ""))

    if not versions:
        return "v1.0.0"

    versions.sort(key=lambda s: list(map(int, s.split("."))))
    latest = versions[-1]

    major, minor, patch = map(int, latest.split("."))

    if bump == "patch":
        patch += 1
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "major":
        major += 1
        minor = 0
        patch = 0

    return f"v{major}.{minor}.{patch}"
