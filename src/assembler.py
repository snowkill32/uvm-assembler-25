import argparse
from pathlib import Path
import re
from bytes import encode_load


CELL = r"mem\s*\[\s*([0-9]+)\s*\]"
INDIRECT = rf"mem\s*\[\s*{CELL}\s*\]"
ASSIGN = r"\s*=\s*"


def parse_line(line):
    """Преобразует одну команду в кортеж полей A, B, C и при наличии D."""
    match = re.fullmatch(rf"{CELL}{ASSIGN}([+-]?[0-9]+)", line)
    if match:
        address, constant = map(int, match.groups())
        return (6, address, constant)

    match = re.fullmatch(
        rf"{CELL}{ASSIGN}mem\s*\[\s*{CELL}\s*\+\s*([0-9]+)\s*\]", line
    )
    if match:
        destination, pointer, offset = map(int, match.groups())
        return (30, pointer, destination, offset)

    match = re.fullmatch(rf"{INDIRECT}{ASSIGN}{CELL}", line)
    if match:
        pointer, source = map(int, match.groups())
        return (5, source, pointer)

    match = re.fullmatch(rf"{INDIRECT}{ASSIGN}sgn\s*\(\s*{CELL}\s*\)", line)
    if match:
        pointer, source = map(int, match.groups())
        return (15, pointer, source)

    raise ValueError(f"неизвестная команда: {line}")


def parse_program(source):
    """Читает исходный файл и возвращает список команд."""
    instructions = []
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    for number, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            instructions.append(parse_line(line))
        except ValueError as error:
            raise ValueError(f"строка {number}: {error}") from error
    return instructions


def main():
    """Собирает двоичный файл и выводит байты в тестовом режиме."""
    parser = argparse.ArgumentParser(description="Ассемблер УВМ, вариант 25")
    parser.add_argument("source", help="путь к тексту программы")
    parser.add_argument("output", help="путь к выходному двоичному файлу")
    parser.add_argument("--test", action="store_true", help="режим тестирования")
    args = parser.parse_args()

    try:
        instructions = parse_program(Path(args.source))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    encoded = []
    for instruction in instructions:
        encoded.append(encode_load(*instruction))
    program_bytes = b"".join(encoded)
    output_path = Path(args.output)
    output_path.write_bytes(program_bytes)

    print(f"Число команд: {len(instructions)}")
    if args.test:
        for instruction in encoded:
            parts = instruction.hex(' ').split()
            word = [f"0x{i.upper()}" for i in parts]
            print(', '.join(word))


if __name__ == "__main__":
    main()
