#include <cstdint>
#include <fstream>
#include <iostream>

int main() {
  // Otwieramy skompresowany plik binarny i plik tekstowy na wynik
  std::ifstream input("dane_int_skompresowane.txt", std::ios::binary);
  std::ofstream output("dane_int_odkodowane.txt");

  if (!input || !output) {
    std::cerr << "Blad: Nie mozna otworzyc plikow." << std::endl;
    return 1;
  }

  unsigned char buffer = 0;  // Tu przechowujemy bajt wczytany z pliku
  int bit_pos = -1;          // Indeks bitu w buforze (od 7 do 0)

  // Pętla główna dekompresji
  while (true) {
    // --- KROK 1: Odczytujemy długość (liczymy jedynki przed zerem) ---
    int length = 0;
    bool end_of_data = false;

    while (true) {
      // Jeśli bufor bitów jest pusty, czytamy nowy bajt z pliku
      if (bit_pos < 0) {
        char c;
        if (!input.get(c)) {
          end_of_data = true;  // Koniec pliku
          break;
        }
        buffer = static_cast<unsigned char>(c);
        bit_pos = 7;  // Zaczynamy od najbardziej znaczącego bitu (z lewej)
      }

      // Pobieramy aktualny bit: przesuwamy bufor w prawo i maskujemy
      int bit = (buffer >> bit_pos) & 1;
      bit_pos--;

      if (bit == 1) {
        length++;  // Każda jedynka zwiększa licznik długości
      } else {
        // Znaleźliśmy 0 (separator)
        break;
      }
    }

    // Jeśli dotarliśmy do końca pliku przed znalezieniem jakichkolwiek jedynek,
    // oznacza to, że skończyły się dane (lub natrafiliśmy na padding)
    if (end_of_data && length == 0) break;

    // --- KROK 2: Odczytujemy wartość (wczytujemy dokładnie 'length' bitów) ---
    uint64_t value = 0;
    for (int i = 0; i < length; ++i) {
      if (bit_pos < 0) {
        char c;
        if (!input.get(c)) break;
        buffer = static_cast<unsigned char>(c);
        bit_pos = 7;
      }

      int bit = (buffer >> bit_pos) & 1;
      bit_pos--;

      // Budujemy liczbę: przesuwamy dotychczasową wartość w lewo i dodajemy bit
      value = (value << 1) | bit;
    }

    // Zapisujemy odkodowaną liczbę do pliku tekstowego
    output << value;

    // Sprawdzamy, czy w pliku binarnym są jeszcze jakieś dane (potencjalne
    // kolejne liczby) Jeśli tak, dodajemy przecinek dla czytelności
    // (opcjonalne)
    if (input.peek() != EOF || bit_pos >= 0) {
      // Podglądamy, czy następne bity to nie tylko same zera dopełnienia
      // (padding) W uproszczonej wersji po prostu dodajemy separator po każdej
      // liczbie
      output << ",";
    } else {
      break;
    }
  }

  input.close();
  output.close();
  std::cout << "Dekompresja zakończona sukcesem!" << std::endl;

  return 0;
}
