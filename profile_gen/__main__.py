from __future__ import annotations

import os
from pathlib import Path

from .build import generate


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    result = generate(root, token=os.environ.get("GITHUB_TOKEN") or None)
    for repo, status in result["statuses"].items():
        print(f"ci {repo}: {status}")
    print(f"wrote {len(result['files'])} files")


if __name__ == "__main__":
    main()
