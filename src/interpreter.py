import argparse
from pathlib import Path
from tempfile import NamedTemporaryFile

MAX_ADDRESS = (1 << 24) - 1
CONSTANT_MASK = (1 << 17) - 1
OFFSET_MASK = (1 << 15) - 1


def parse_address_range(text):
    """Читает включительный диапазон адресов для дампа."""
    try:
        start, end = map(int, text.split(":"))
    except ValueError as error:
        raise argparse.ArgumentTypeError("формат: START:END") from error
    if not 0 <= start <= end <= MAX_ADDRESS:
        raise argparse.ArgumentTypeError(
            f"ожидается 0 <= начало <= конец <= {MAX_ADDRESS}"
        )
    return start, end


def write_memory_dump(path, memory, addresses):
    """Записывает ячейки памяти из указанного диапазона в XML."""
    start, end = addresses
    stream = NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
    )
    temporary_path = Path(stream.name)
    try:
        with stream:
            stream.write('<?xml version="1.0" encoding="utf-8"?>\n')
            stream.write("<memory>\n")
            for address in range(start, end + 1):
                value = memory.get(address, 0)
                stream.write(f'  <cell address="{address}">{value}</cell>\n')
            stream.write("</memory>\n")
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


parser = argparse.ArgumentParser(description="Интерпретатор УВМ, вариант 25")
parser.add_argument("program", type=Path, help="путь к двоичной программе")
parser.add_argument("dump", type=Path, help="путь к выходному XML-файлу")
parser.add_argument(
    "addresses",
    type=parse_address_range,
    metavar="START:END",
    help="диапазон адресов для дампа, включительно",
)
args = parser.parse_args()

try:
    data = args.program.read_bytes()
except OSError as error:
    parser.error(str(error))

offset = 0
sizes = {6: 6, 5: 7, 15: 7, 30: 9}
memory = {}
for index in range(len(data)):
    memory[index] = data[index]
while offset < len(data):
    first_byte = memory[offset]
    opcode = first_byte & 0b11111
    size = sizes[opcode]
    command_bytes = []
    for i in range(offset, offset + size):
        command_bytes.append(memory[i])
    print(command_bytes)
    cmd = int.from_bytes(command_bytes, "little")
    field_c = cmd >> 29 & 0b111111111111111111111111
    if opcode == 6:
        field_b = cmd >> 5 & 0b111111111111111111111111
        field_c = cmd >> 29 & CONSTANT_MASK
        fields = (opcode, field_b, field_c)
        memory[field_b] = field_c
    elif opcode == 5:
        field_b = cmd >> 5 & 0b111111111111111111111111
        fields = (opcode, field_b, field_c)
        destination_address = memory.get(field_c, 0)
        value = memory.get(field_b, 0)
        memory[destination_address] = value
        print(memory[destination_address])
    elif opcode == 15:
        field_b = cmd >> 5 & 0b111111111111111111111111
        fields = (opcode, field_b, field_c)
    elif opcode == 30:
        field_b = cmd >> 5 & 0b111111111111111111111111
        field_c = cmd >> 29 & 0b111111111111111111111111
        field_d = cmd >> 53 & OFFSET_MASK
        fields = (opcode, field_b, field_c, field_d)
        base_address = memory.get(field_b, 0)
        source_address = base_address + field_d
        value = memory.get(source_address, 0)
        memory[field_c] = value
        print(memory[field_c])

    print(fields)
    offset += size

try:
    write_memory_dump(args.dump, memory, args.addresses)
except OSError as error:
    parser.error(str(error))
