#! /usr/bin/python3

import argparse
from datetime import datetime, timezone, timedelta
import subprocess
from typing import Tuple


def get_author_and_timestamp(file: str, line_number: int) -> Tuple[str, str, str]:
    # Use --porcelain for machine-readable output! No regex needed.
    result = subprocess.run(
        ["git", "blame", "--porcelain", "-L", f"{line_number},+1", "--", file],
        capture_output=True,
        text=True,
        check=True,  # Throw error if file/line bad
    )

    lines = result.stdout.splitlines()

    # First line is always: <commit-hash> <orig_line> <final_line> [group_lines]
    commit_hash = lines[0].split()[0]

    author = "Unknown"
    epoch_time = 0
    tz_offset = "+0000"

    # Parse key-value headers
    for line in lines[1:]:
        if line.startswith("author "):
            author = line[7:]
        elif line.startswith("author-time "):
            epoch_time = int(line[12:])
        elif line.startswith("author-tz "):
            tz_offset = line[10:]
        elif line.startswith("\t"):  # Code line starts with tab, metadata done
            break

    # Format timestamp nicely (YYYY-MM-DD HH:MM:SS +ZZZZ)
    hours = int(tz_offset[:3])
    minutes = int(tz_offset[0] + tz_offset[3:])
    tz = timezone(timedelta(hours=hours, minutes=minutes))
    dt_str = datetime.fromtimestamp(epoch_time, tz=tz).strftime("%Y-%m-%d %H:%M:%S %z")

    return commit_hash, author, dt_str


def get_commit_msg(commit_hash: str) -> str:
    # Use %B to get full commit message body
    result = subprocess.run(
        ["git", "log", "--format=%B", "-n", "1", commit_hash],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("file", type=str, help="Path to file")
    parser.add_argument("line_number", type=int, help="Line number to blame")

    args = parser.parse_args()

    try:
        commit_hash, author, dt_str = get_author_and_timestamp(args.file, args.line_number)
        commit_msg = get_commit_msg(commit_hash)

        print(f'[{author}] [{dt_str}] [{commit_hash[:8]}] "{commit_msg}"')
    except subprocess.CalledProcessError as e:
        print(f"Error running git: {e.stderr.strip()}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
