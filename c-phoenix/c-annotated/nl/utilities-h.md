# Utility Declarations (`utilities.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat de geannoteerde header-declaraties voor [`utilities.h`](../../utilities.h).

---

## Declaraties & Koppelingen
- `check_input_bits(uint8_t mask)`: Flankdetectie voor drukknopen.
- `print_number(uint16_t screen_addr, uint16_t data_addr, uint8_t digits)`: BCD-cijfers afdrukken.
- `print_text_lines(uint16_t addr, uint8_t count)`: Tekstregels afdrukken.
- `right_one_column(uint16_t de)` / `left_one_column(uint16_t de)`: VRAM 1 kolom opschuiven (`+0x20` / `-0x20`).
- `mem_read(uint16_t addr)` / `mem_write(uint16_t addr, uint8_t val)`: RAM lees-/schrijfbeveiliging.

#### **Knowledge Graph Koppelingen**
* **Overeenkomstige C-implementatie:** [`utilities.c`](../../utilities.c) $\rightarrow$ [`utilities.md`](utilities.md)
