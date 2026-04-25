import heapq
import itertools
import math
from typing import Iterable

import matplotlib.pyplot as plt

def calculate_huffman_avg_length(probs):
    """
    Simulates Huffman coding using a priority queue to find the 
    weighted average codeword length.
    """
    # Use a min-heap to store probabilities
    heap = [[p] for p in probs]
    heapq.heapify(heap)
    
    avg_length = 0.0
    
    # Huffman algorithm: repeatedly combine the two smallest probabilities
    while len(heap) > 1:
        low1 = heapq.heappop(heap)
        low2 = heapq.heappop(heap)
        
        combined_prob = sum(low1) + sum(low2)
        # The internal node's probability contributes to the total path length
        avg_length += combined_prob
        heapq.heappush(heap, [combined_prob])
        
    return avg_length

def bits_per_symbol_for_length(p0: float, p1: float, n: int) -> float:
    probs = []
    for seq in itertools.product([p0, p1], repeat=n):
        prob = 1.0
        for symbol_prob in seq:
            prob *= symbol_prob
        probs.append(prob)

    avg_len_sequence = calculate_huffman_avg_length(probs)
    return avg_len_sequence / n


def bits_per_symbol_curve(p0: float, max_n: int) -> list[float]:
    p1 = 1.0 - p0
    return [bits_per_symbol_for_length(p0, p1, n) for n in range(1, max_n + 1)]


def entropy_limit(p0: float) -> float:
    p1 = 1.0 - p0
    return -(p0 * math.log2(p0) + p1 * math.log2(p1))


def generate_huffman_table(p0: float, max_n: int):
    p1 = 1.0 - p0
    print(f"{'n (Length)':<12} | {'Avg Bits/Sequence':<18} | {'Bits/Symbol':<15}")
    print("-" * 50)

    for n in range(1, max_n + 1):
        bits_per_symbol = bits_per_symbol_for_length(p0, p1, n)
        avg_len_sequence = bits_per_symbol * n
        
        print(f"{n:<12} | {avg_len_sequence:<18.5f} | {bits_per_symbol:<15.5f}")

    entropy = entropy_limit(p0)
    print("-" * 50)
    print(f"Theoretical Entropy Limit: {entropy:.5f} bits/symbol")


def plot_bits_vs_length(p_zero_values: Iterable[float], max_len: int, output_path: str):
    plt.figure(figsize=(8, 5))
    x = list(range(1, max_len + 1))
    first = True
    for p0 in p_zero_values:
        y = bits_per_symbol_curve(p0, max_len)
        plt.plot(x, y, marker="o", linewidth=1.6, label=f"P_ZERO={p0:.2f}")
        plt.hlines(
            y=entropy_limit(p0),
            xmin=1,
            xmax=max_len,
            linestyles="--",
            linewidth=1.2,
            alpha=0.5,
            colors="gray",
            label="theoretical limit" if first else None,
        )
        first = False

    plt.title("Huffman Bits/Symbol vs Sequence Length")
    plt.xlabel("Sequence length (n)")
    plt.ylabel("Bits per symbol")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def plot_bits_vs_pzero(
    p_zero_values: Iterable[float], max_lens: Iterable[int], output_path: str
):
    plt.figure(figsize=(8, 5))
    p_zero_values = list(p_zero_values)
    for max_len in max_lens:
        y = [bits_per_symbol_for_length(p0, 1.0 - p0, max_len) for p0 in p_zero_values]
        plt.plot(p_zero_values, y, marker="o", linewidth=1.6, label=f"max_len={max_len}")
    entropy_curve = [entropy_limit(p0) for p0 in p_zero_values]
    plt.plot(
        p_zero_values,
        entropy_curve,
        linestyle="--",
        linewidth=2.0,
        color="black",
        label="theoretical limit",
    )

    plt.title("Huffman Bits/Symbol vs P_ZERO")
    plt.xlabel("P_ZERO")
    plt.ylabel("Bits per symbol (at n=max_len)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


if __name__ == "__main__":
    # Parameters for table output
    P_ZERO = 0.75
    MAX_SEQUENCE_LENGTH = 10

    # Parameter sweeps for plots
    P_ZERO_VALUES = [0.50, 0.60, 0.70, 0.75, 0.80, 0.90]
    MAX_LEN_VALUES = [2, 3, 4, 6, 8, 10]
    P_ZERO_SWEEP = [round(v, 2) for v in [0.50 + i * 0.05 for i in range(9)]]

    generate_huffman_table(P_ZERO, MAX_SEQUENCE_LENGTH)

    plot_bits_vs_length(
        p_zero_values=P_ZERO_VALUES,
        max_len=MAX_SEQUENCE_LENGTH,
        output_path="huffman_bits_per_symbol_vs_length.png",
    )
    plot_bits_vs_pzero(
        p_zero_values=P_ZERO_SWEEP,
        max_lens=MAX_LEN_VALUES,
        output_path="huffman_bits_per_symbol_vs_pzero.png",
    )
