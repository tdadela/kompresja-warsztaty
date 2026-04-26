from collections import Counter


def get_normalized_frequencies(text, M):
    """
    Counts symbols and scales frequencies so they sum to M.
    """
    counts = Counter(text)
    total = len(text)
    freqs = {}

    # Scale frequencies
    current_sum = 0
    for char, count in counts.items():
        # Ensure every present character has at least 1/M frequency
        f = max(1, int((count / total) * M))
        freqs[char] = f
        current_sum += f

    # Adjust last element to ensure the sum is exactly M
    last_char = list(counts.keys())[-1]
    freqs[last_char] += M - current_sum

    # Build cumulative frequencies (offsets)
    cum_freqs = {}
    offset = 0
    for char in sorted(freqs.keys()):
        cum_freqs[char] = offset
        offset += freqs[char]

    return freqs, cum_freqs


def rans_encode(text, freqs, cum_freqs, M):
    """
    Encodes text into a single state integer x.
    """
    # x must start >= M. Starting at M is standard.
    x = M

    # We encode symbols one by one.
    # Note: rANS is LIFO, so we encode in normal order and decode in reverse.
    for char in text:
        f = freqs[char]
        b = cum_freqs[char]

        # Core rANS encoding formula:
        # x_next = floor(x / f) * M + (x % f) + b
        x = (x // f) * M + (x % f) + b

    return x


def rans_decode(state, freqs, cum_freqs, M, length):
    """
    Decodes the state integer back into text.
    """
    x = state
    decoded_chars = []

    # Create a reverse lookup for cumulative frequencies
    sorted_chars = sorted(freqs.keys())

    for _ in range(length):
        # 1. Determine which symbol corresponds to the current slot
        slot = x % M

        # Find char s such that cum_freqs[s] <= slot < cum_freqs[s+1]
        char_s = None
        for char in sorted_chars:
            if cum_freqs[char] <= slot < cum_freqs[char] + freqs[char]:
                char_s = char
                break

        decoded_chars.append(char_s)

        # 2. Update state to "remove" the symbol
        f = freqs[char_s]
        b = cum_freqs[char_s]

        # Core rANS decoding formula:
        # x_prev = f * floor(x / M) + (x % M) - b
        x = f * (x // M) + (x % M) - b

    # Because rANS is LIFO, the decoded sequence is reversed.
    return "".join(reversed(decoded_chars))


# --- Example Usage ---
if __name__ == "__main__":
    message = "banana"
    # M is the 'precision' or 'scale'. Usually a power of 2.
    M = 1024

    print(f"Original Message: {message}")

    # 1. Setup Probabilities
    freqs, cum_freqs = get_normalized_frequencies(message, M)

    # 2. Encode
    compressed_state = rans_encode(message, freqs, cum_freqs, M)
    print(f"Encoded State (Large Int): {compressed_state}")

    # 3. Decode
    restored_message = rans_decode(compressed_state, freqs, cum_freqs, M, len(message))
    print(f"Decoded Message: {restored_message}")
