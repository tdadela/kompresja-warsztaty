#!/usr/bin/env python3
import argparse
from pathlib import Path


def parse_values(text: str):
    # Input supports commas and spaces, e.g. "42, 99 7"
    return [int(token) for token in text.replace(",", " ").split()]


def compress(input_path: Path, output_path: Path):
    text = input_path.read_text(encoding="utf-8")
    values = parse_values(text)
    bits = []

    # Encode each number as: [length x '1'] + ['0'] + [value bits]
    for value in values:
        length = value.bit_length() if value != 0 else 1

        bits.extend([1] * length)
        bits.append(0)

        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)

    # Pack bits into bytes and pad the last byte with zeros on the right.
    packed = bytearray()
    for start in range(0, len(bits), 8):
        byte_bits = bits[start : start + 8]
        while len(byte_bits) < 8:
            byte_bits.append(0)

        byte = 0
        for bit in byte_bits:
            byte = (byte << 1) | bit
        packed.append(byte)

    output_path.write_bytes(bytes(packed))


def decompress(input_path: Path, output_path: Path):
    data = input_path.read_bytes()
    bits = []
    for byte in data:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)

    values = []
    i = 0
    n = len(bits)
    while i < n:
        # Read unary length: count 1s until first 0.
        length = 0
        while i < n and bits[i] == 1:
            length += 1
            i += 1

        # No separator => only padding left.
        if i >= n:
            break

        # Consume separator 0.
        i += 1

        # length == 0 cannot be a valid number here, treat as padding.
        if length == 0:
            break

        if i + length > n:
            break

        value = 0
        for _ in range(length):
            value = (value << 1) | bits[i]
            i += 1
        values.append(value)

    output_path.write_text(",".join(str(v) for v in values), encoding="utf-8")
    print("Dekompresja zakonczona sukcesem!")


def main():
    parser = argparse.ArgumentParser(description="Integer compressor/decompressor.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compress_parser = subparsers.add_parser("compress")
    compress_parser.add_argument("-i", "--input", default="dane_int.txt")
    compress_parser.add_argument("-o", "--output", default="dane_int_skompresowane.txt")

    decompress_parser = subparsers.add_parser("decompress")
    decompress_parser.add_argument(
        "-i", "--input", default="dane_int_skompresowane.txt"
    )
    decompress_parser.add_argument("-o", "--output", default="dane_int_odkodowane.txt")

    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if args.command == "compress":
        compress(input_path, output_path)
    else:
        decompress(input_path, output_path)


if __name__ == "__main__":
    main()
