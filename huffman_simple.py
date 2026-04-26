#!/usr/bin/env python3
from __future__ import annotations

import argparse
import heapq
from collections import Counter
from pathlib import Path


# Node is represented as (symbol, left, right)
# - symbol is int 0..255 for leaves
# - symbol is None for internal nodes

def build_tree(freq: dict[int, int]):
    heap = []
    order = 0

    for symbol, count in sorted(freq.items()):
        heapq.heappush(heap, (count, order, (symbol, None, None)))
        order += 1

    if not heap:
        return None

    while len(heap) > 1:
        c1, _, n1 = heapq.heappop(heap)
        c2, _, n2 = heapq.heappop(heap)
        parent = (None, n1, n2)
        heapq.heappush(heap, (c1 + c2, order, parent))
        order += 1

    return heap[0][2]


def build_codes(node, prefix: str = "", codes: dict[int, str] | None = None):
    if codes is None:
        codes = {}

    if node is None:
        return codes

    symbol, left, right = node

    if symbol is not None:
        # Single-symbol file gets code "0".
        codes[symbol] = prefix or "0"
        return codes

    build_codes(left, prefix + "0", codes)
    build_codes(right, prefix + "1", codes)
    return codes


def compress(input_path: Path, output_path: Path) -> None:
    data = input_path.read_bytes()
    freq = dict(Counter(data))
    tree = build_tree(freq)
    codes = build_codes(tree)

    bits = "".join(codes[b] for b in data)

    # Very simple teaching format:
    # HUFFMAN_SIMPLE\n
    # <original_size>\n
    # <unique_symbols>\n
    # <byte> <freq>\n  repeated
    # DATA\n
    # <bitstring>
    with output_path.open("w", encoding="utf-8") as f:
        f.write("HUFFMAN_SIMPLE\n")
        f.write(f"{len(data)}\n")
        f.write(f"{len(freq)}\n")
        for symbol, count in sorted(freq.items()):
            f.write(f"{symbol} {count}\n")
        f.write("DATA\n")
        f.write(bits)

    print(f"Compressed {input_path} -> {output_path}")


def decompress(input_path: Path, output_path: Path) -> None:
    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) < 4 or lines[0] != "HUFFMAN_SIMPLE":
        raise ValueError("Invalid format")

    original_size = int(lines[1])
    unique = int(lines[2])

    freq: dict[int, int] = {}
    idx = 3
    for _ in range(unique):
        symbol_s, count_s = lines[idx].split()
        freq[int(symbol_s)] = int(count_s)
        idx += 1

    if lines[idx] != "DATA":
        raise ValueError("Invalid format: missing DATA marker")

    # bitstring is everything after DATA line (joined, in case editors wrapped it)
    bits = "".join(lines[idx + 1 :])

    if original_size == 0:
        output_path.write_bytes(b"")
        print(f"Decompressed {input_path} -> {output_path}")
        return

    tree = build_tree(freq)
    if tree is None:
        raise ValueError("Invalid format: empty tree")

    symbol, left, right = tree
    if symbol is not None:
        output_path.write_bytes(bytes([symbol]) * original_size)
        print(f"Decompressed {input_path} -> {output_path}")
        return

    out = bytearray()
    node = tree

    for bit in bits:
        _, l, r = node
        node = l if bit == "0" else r
        s, _, _ = node

        if s is not None:
            out.append(s)
            if len(out) == original_size:
                break
            node = tree

    if len(out) != original_size:
        raise ValueError("Invalid bitstream: decoded size mismatch")

    output_path.write_bytes(bytes(out))
    print(f"Decompressed {input_path} -> {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple Huffman compressor/decompressor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_comp = subparsers.add_parser("compress")
    p_comp.add_argument("-i", "--input", default="alice29.txt")
    p_comp.add_argument("-o", "--output", default="alice29_simple.huf")

    p_decomp = subparsers.add_parser("decompress")
    p_decomp.add_argument("-i", "--input", default="alice29_simple.huf")
    p_decomp.add_argument("-o", "--output", default="alice29_simple.decoded.txt")

    args = parser.parse_args()

    if args.command == "compress":
        compress(Path(args.input), Path(args.output))
    else:
        decompress(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
