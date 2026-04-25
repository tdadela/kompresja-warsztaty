#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <iomanip>

/**
 * Basic Node structure to serve as a base for Huffman Tree construction.
 */
struct Node {
    char symbol;
    size_t frequency;
    Node *left, *right;

    Node(char s, size_t f) : symbol(s), frequency(f), left(nullptr), right(nullptr) {}
};

/**
 * Helper to display non-printable characters visually, 
 * similar to format_char in your Python script.
 */
std::string formatChar(char ch) {
    switch (ch) {
        case '\n': return "\\n";
        case '\t': return "\\t";
        case ' ':  return "[space]";
        default:   return std::string(1, ch);
    }
}

int main(int argc, char* argv[]) {
    // 1. Handle command line arguments
    std::string filename = (argc > 1) ? argv[1] : "alice29.txt";
    
    std::ifstream inputFile(filename, std::ios::binary);
    if (!inputFile.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return 1;
    }

    // 2. Count frequencies
    // Using a map is the C++ equivalent of Python's Counter
    std::map<char, size_t> frequencies;
    char ch;
    size_t totalChars = 0;

    while (inputFile.get(ch)) {
        frequencies[ch]++;
        totalChars++;
    }
    inputFile.close();

    // 3. Transfer to a vector for sorting (similar to counts.most_common())
    std::vector<std::pair<char, size_t>> sortedFreqs(frequencies.begin(), frequencies.end());
    
    std::sort(sortedFreqs.begin(), sortedFreqs.end(), [](const auto& a, const auto& b) {
        return a.second > b.second; // Descending order
    });

    // 4. Output Statistics
    std::cout << "File: " << filename << "\n";
    std::cout << "Number of characters: " << totalChars << "\n";
    std::cout << "Unique characters: " << frequencies.size() << "\n";
    std::cout << "--------------------------------\n";
    std::cout << std::left << std::setw(10) << "Char" << "Frequency" << "\n";
    std::cout << "--------------------------------\n";

    for (const auto& pair : sortedFreqs) {
        std::cout << std::left << std::setw(10) << formatChar(pair.first) 
                  << pair.second << "\n";
    }

    return 0;
}
