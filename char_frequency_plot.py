#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count characters in a text file and plot character frequencies."
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="alice29.txt",
        help="Path to input text file (default: alice29.txt)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Number of most frequent characters to show (0 means all; default: 0)",
    )
    parser.add_argument(
        "--out",
        default="char_frequency.png",
        help="Output image path for the plot (default: char_frequency.png)",
    )
    return parser.parse_args()


def format_char(ch: str) -> str:
    if ch == "\n":
        return "\\n"
    if ch == "\t":
        return "\\t"
    if ch == " ":
        return "[space]"
    return ch


def main() -> None:
    args = parse_args()
    path = Path(args.file)

    text = path.read_text(encoding="utf-8", errors="replace")
    total_chars = len(text)
    counts = Counter(text)

    print(f"File: {path}")
    print(f"Number of characters: {total_chars}")
    print(f"Unique characters: {len(counts)}")

    if args.top <= 0:
        top_items = counts.most_common()
        title_scope = f"All {len(top_items)}"
    else:
        top_items = counts.most_common(args.top)
        title_scope = f"Top {len(top_items)}"

    labels = [format_char(ch) for ch, _ in top_items]
    values = [freq for _, freq in top_items]

    plt.figure(figsize=(14, 6))
    plt.bar(labels, values)
    plt.title(f"{title_scope} Character Frequencies in {path.name}")
    plt.xlabel("Character")
    plt.ylabel("Frequency")
    plt.xticks(rotation=75, ha="right")
    plt.tight_layout()
    plt.savefig(args.out, dpi=160)

    print(f"Saved plot to: {args.out}")


if __name__ == "__main__":
    main()
