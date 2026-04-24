#include <iostream>
#include <fstream>
#include <cstdint>

int main() {
    // Otwieramy plik wejściowy (tekstowy) i wyjściowy (binarny)
    std::ifstream input("dane_int.txt");
    std::ofstream output("dane_int_skompresowane.txt", std::ios::binary);

    if (!input || !output) {
        std::cerr << "Blad: Nie udalo sie otworzyc plikow." << std::endl;
        return 1;
    }

    // Zmienne do "pakowania" bitów w bajty
    unsigned char buffer = 0; // Tu składamy bity, aż powstanie pełny bajt (8 bitów)
    int bit_count = 0;        // Licznik mówi nam, ile bitów jest już w buforze
    uint64_t value;           // Zmienna na wczytaną liczbę

    // Główna pętla: czytamy liczby oddzielone przecinkami lub spacjami
    while (input >> value) {

        // --- KROK 1: Obliczanie długości liczby (ile bitów zajmuje) ---
        int length = 0;
        if (value == 0) {
            length = 1;
        } else {
            uint64_t temp = value;
            while (temp > 0) {
                temp >>= 1; // Przesunięcie w prawo (dzielenie przez 2) usuwa ostatni bit
                length++;   // Liczymy, ile razy udało się przesunąć
            }
        }

        // --- KROK 2: Zapisywanie prefiksu (jedynki w ilości równej 'length') ---
        for (int i = 0; i < length; ++i) {
            // Przesuwamy zawartość bufora o 1 w lewo i wstawiamy 1 na koniec
            buffer = (buffer << 1) | 1;
            bit_count++;

            // Jeśli bufor ma 8 bitów, wysyłamy go do pliku
            if (bit_count == 8) {
                output.put(static_cast<char>(buffer));
                buffer = 0;
                bit_count = 0;
            }
        }

        // --- KROK 3: Zapisywanie separatora (pojedyncze zero) ---
        // Robimy miejsce przesuwając w lewo, na końcu naturalnie pojawi się 0
        buffer = (buffer << 1) | 0;
        bit_count++;

        if (bit_count == 8) {
            output.put(static_cast<char>(buffer));
            buffer = 0;
            bit_count = 0;
        }

        // --- KROK 4: Zapisywanie samej liczby na 'length' bitach ---
        for (int i = length - 1; i >= 0; --i) {
            // (value >> i) & 1 wyciąga i-ty bit liczby (od najstarszego)
            int bit = (value >> i) & 1;

            buffer = (buffer << 1) | bit;
            bit_count++;

            if (bit_count == 8) {
                output.put(static_cast<char>(buffer));
                buffer = 0;
                bit_count = 0;
            }
        }
        // Ignorujemy przecinek, jeśli występuje w pliku tekstowym
        if (input.peek() == ',') {
            input.ignore();
        }
    }
    // --- KROK 5 ---
    // Jeśli po zakończeniu pętli w buforze zostały jakieś bity (mniej niż 8)
    if (bit_count > 0) {
        // Musimy je "dosunąć" do lewej krawędzi bajtu (uzupełnić zerami z prawej)
        buffer <<= (8 - bit_count);
        output.put(static_cast<char>(buffer));
    }
    input.close();
    output.close();

    return 0;
}