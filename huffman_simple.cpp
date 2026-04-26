#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Node {
    int symbol; // 0..255 for leaf, -1 for internal
    std::shared_ptr<Node> left;
    std::shared_ptr<Node> right;
};

struct HeapItem {
    uint64_t freq;
    int order;
    std::shared_ptr<Node> node;
};

struct Cmp {
    bool operator()(const HeapItem& a, const HeapItem& b) const {
        if (a.freq != b.freq) {
            return a.freq > b.freq;
        }
        return a.order > b.order;
    }
};

std::shared_ptr<Node> build_tree(const std::array<uint32_t, 256>& freq) {
    std::priority_queue<HeapItem, std::vector<HeapItem>, Cmp> pq;
    int order = 0;

    for (int s = 0; s < 256; ++s) {
        if (freq[s] == 0) {
            continue;
        }
        auto leaf = std::make_shared<Node>();
        leaf->symbol = s;
        pq.push({freq[s], order++, leaf});
    }

    if (pq.empty()) {
        return nullptr;
    }

    while (pq.size() > 1) {
        HeapItem a = pq.top();
        pq.pop();
        HeapItem b = pq.top();
        pq.pop();

        auto parent = std::make_shared<Node>();
        parent->symbol = -1;
        parent->left = a.node;
        parent->right = b.node;

        pq.push({a.freq + b.freq, order++, parent});
    }

    return pq.top().node;
}

void build_codes(const std::shared_ptr<Node>& node, const std::string& prefix,
                 std::array<std::string, 256>& codes) {
    if (!node) {
        return;
    }

    if (node->symbol >= 0) {
        codes[node->symbol] = prefix.empty() ? "0" : prefix;
        return;
    }

    build_codes(node->left, prefix + "0", codes);
    build_codes(node->right, prefix + "1", codes);
}

std::vector<uint8_t> read_bytes(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        throw std::runtime_error("Cannot open input: " + path);
    }

    in.seekg(0, std::ios::end);
    std::streamsize size = in.tellg();
    in.seekg(0, std::ios::beg);

    std::vector<uint8_t> data(static_cast<size_t>(size));
    if (size > 0) {
        in.read(reinterpret_cast<char*>(data.data()), size);
    }
    return data;
}

void write_bytes(const std::string& path, const std::vector<uint8_t>& data) {
    std::ofstream out(path, std::ios::binary);
    if (!out) {
        throw std::runtime_error("Cannot open output: " + path);
    }
    if (!data.empty()) {
        out.write(reinterpret_cast<const char*>(data.data()), static_cast<std::streamsize>(data.size()));
    }
}

void compress_file(const std::string& input_path, const std::string& output_path) {
    std::vector<uint8_t> data = read_bytes(input_path);

    std::array<uint32_t, 256> freq{};
    for (uint8_t b : data) {
        ++freq[b];
    }

    std::shared_ptr<Node> tree = build_tree(freq);
    std::array<std::string, 256> codes;
    build_codes(tree, "", codes);

    std::string bits;
    bits.reserve(data.size() * 4);
    for (uint8_t b : data) {
        bits += codes[b];
    }

    std::ofstream out(output_path);
    if (!out) {
        throw std::runtime_error("Cannot open output: " + output_path);
    }

    out << "HUFFMAN_SIMPLE\n";
    out << data.size() << "\n";

    int unique = 0;
    for (uint32_t f : freq) {
        if (f > 0) {
            ++unique;
        }
    }
    out << unique << "\n";

    for (int s = 0; s < 256; ++s) {
        if (freq[s] > 0) {
            out << s << " " << freq[s] << "\n";
        }
    }

    out << "DATA\n";
    out << bits;

    std::cout << "Compressed " << input_path << " -> " << output_path << "\n";
}

void decompress_file(const std::string& input_path, const std::string& output_path) {
    std::ifstream in(input_path);
    if (!in) {
        throw std::runtime_error("Cannot open input: " + input_path);
    }

    std::string line;

    std::getline(in, line);
    if (line != "HUFFMAN_SIMPLE") {
        throw std::runtime_error("Invalid format");
    }

    std::getline(in, line);
    uint64_t original_size = std::stoull(line);

    std::getline(in, line);
    int unique = std::stoi(line);

    std::array<uint32_t, 256> freq{};
    for (int i = 0; i < unique; ++i) {
        std::getline(in, line);
        std::istringstream iss(line);
        int symbol = 0;
        uint32_t count = 0;
        iss >> symbol >> count;
        if (!iss || symbol < 0 || symbol > 255) {
            throw std::runtime_error("Invalid frequency entry");
        }
        freq[symbol] = count;
    }

    std::getline(in, line);
    if (line != "DATA") {
        throw std::runtime_error("Invalid format: missing DATA");
    }

    std::string bits;
    while (std::getline(in, line)) {
        bits += line;
    }

    if (original_size == 0) {
        write_bytes(output_path, {});
        std::cout << "Decompressed " << input_path << " -> " << output_path << "\n";
        return;
    }

    std::shared_ptr<Node> tree = build_tree(freq);
    if (!tree) {
        throw std::runtime_error("Invalid format: empty tree");
    }

    if (tree->symbol >= 0) {
        std::vector<uint8_t> out(static_cast<size_t>(original_size), static_cast<uint8_t>(tree->symbol));
        write_bytes(output_path, out);
        std::cout << "Decompressed " << input_path << " -> " << output_path << "\n";
        return;
    }

    std::vector<uint8_t> out;
    out.reserve(static_cast<size_t>(original_size));

    std::shared_ptr<Node> node = tree;
    for (char bit : bits) {
        node = (bit == '0') ? node->left : node->right;

        if (node->symbol >= 0) {
            out.push_back(static_cast<uint8_t>(node->symbol));
            if (out.size() == original_size) {
                break;
            }
            node = tree;
        }
    }

    if (out.size() != original_size) {
        throw std::runtime_error("Invalid bitstream: decoded size mismatch");
    }

    write_bytes(output_path, out);
    std::cout << "Decompressed " << input_path << " -> " << output_path << "\n";
}

void usage(const char* prog) {
    std::cerr << "Usage:\n"
              << "  " << prog << " compress [input] [output]\n"
              << "  " << prog << " decompress [input] [output]\n"
              << "Defaults:\n"
              << "  compress:   alice29.txt -> alice29_simple_cpp.huf\n"
              << "  decompress: alice29_simple_cpp.huf -> alice29_simple_cpp.decoded.txt\n";
}

int main(int argc, char** argv) {
    try {
        if (argc < 2) {
            usage(argv[0]);
            return 1;
        }

        std::string mode = argv[1];

        if (mode == "compress") {
            std::string input = (argc >= 3) ? argv[2] : "alice29.txt";
            std::string output = (argc >= 4) ? argv[3] : "alice29_simple_cpp.huf";
            compress_file(input, output);
            return 0;
        }

        if (mode == "decompress") {
            std::string input = (argc >= 3) ? argv[2] : "alice29_simple_cpp.huf";
            std::string output = (argc >= 4) ? argv[3] : "alice29_simple_cpp.decoded.txt";
            decompress_file(input, output);
            return 0;
        }

        usage(argv[0]);
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
}
