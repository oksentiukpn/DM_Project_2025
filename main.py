#!/usr/bin/env python3
"""
Приклад main.py скрипту для демонстрації
Замініть цей файл своїм реальним main.py

Скрипт повинен:
1. Приймати шлях до файлу як перший аргумент
2. Опціонально приймати --verbose
3. Повертати JSON масив, де індекс = номер рядка, значення = номер стовпця
"""

import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Process a file')
    parser.add_argument('file', help='Path to the file to process')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    if args.verbose:
        print(f"Processing file: {args.file}", file=sys.stderr)

    # Приклад результату: для рядка 0 -> стовпець 1, рядка 1 -> стовпець 3, і т.д.
    # Замініть це на вашу реальну логіку обробки
    result = [1, 3, 0, 2, 4, 1, 2]

    # ВАЖЛИВО: виводимо результат як JSON
    print(json.dumps(result))

if __name__ == '__main__':
    main()
