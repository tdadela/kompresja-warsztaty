import heapq
import itertools
import math

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

def generate_huffman_table(p0, p1, max_n):
    print(f"{'n (Length)':<12} | {'Avg Bits/Sequence':<18} | {'Bits/Symbol':<15}")
    print("-" * 50)

    for n in range(1, max_n + 1):
        # Generate probabilities for all 2^n possible sequences
        # Example for n=2: (p0*p0, p0*p1, p1*p0, p1*p1)
        probs = []
        for seq in itertools.product([p0, p1], repeat=n):
            prob = 1.0
            for symbol_prob in seq:
                prob *= symbol_prob
            probs.append(prob)
        
        avg_len_sequence = calculate_huffman_avg_length(probs)
        bits_per_symbol = avg_len_sequence / n
        
        print(f"{n:<12} | {avg_len_sequence:<18.5f} | {bits_per_symbol:<15.5f}")

    entropy = -(p0 * math.log2(p0) + p1 * math.log2(p1))
    print("-" * 50)
    print(f"Theoretical Entropy Limit: {entropy:.5f} bits/symbol")

# Parameters
P_ZERO = 0.75
P_ONE = 0.25
MAX_SEQUENCE_LENGTH = 10

generate_huffman_table(P_ZERO, P_ONE, MAX_SEQUENCE_LENGTH)
