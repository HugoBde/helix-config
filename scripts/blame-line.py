#! /usr/bin/python3

import argparse
import re
import subprocess
from typing import Tuple


def get_author_and_timestamp(file: str, line_number: int) -> Tuple[str, str, str]:
    text = subprocess.run(
        ["git", "blame", "-L", f"{line_number},+1", file],
        capture_output=True,
        text=True,
    ).stdout

    commit_hash, author, datetime = re.search(
        r"^([0-9a-f^]+)\s+\((.+?)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+[-+]\d{4})",
        text,
    ).groups()

    return commit_hash, author, datetime


def get_commit_msg(commit_hash: str) -> str:
    text = subprocess.run(
        ["git", "log", "--format=%B", "-n", "1", commit_hash],
        capture_output=True,
        text=True,
    ).stdout
    return text


def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "file",
        type=str,
    )

    parser.add_argument("line_number", type=int)

    args = parser.parse_args()

    commit_hash, author, datetime = get_author_and_timestamp(
        args.file, args.line_number
    )
    commit_msg = get_commit_msg(commit_hash)

    print(f"[{author}] [{datetime}] [{commit_hash}] {commit_msg}".strip())


if __name__ == "__main__":
    main()
