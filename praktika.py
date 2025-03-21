import os  # Работа с файловой системой
import sys  # Работа с аргументами командной строки
import secrets  # Генерация случайных данных
from typing import List  # Типизация с использованием List

# S-box из ГОСТ Р 34.12-2015, Приложение А
SBOX = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 11, 7, 13, 0, 4, 15, 14],
    [7, 11, 5, 8, 12, 4, 2, 0, 14, 1, 3, 10, 9, 15, 6, 13],
    [13, 1, 7, 4, 11, 5, 0, 15, 3, 12, 14, 6, 9, 10, 2, 8],
    [5, 10, 15, 12, 1, 13, 14, 11, 8, 3, 6, 0, 4, 7, 9, 2],
    [14, 5, 0, 15, 13, 11, 3, 6, 9, 2, 12, 7, 1, 8, 10, 4],
    [11, 13, 12, 3, 7, 14, 10, 5, 0, 9, 4, 15, 2, 8, 1, 6],
    [15, 12, 9, 7, 3, 0, 11, 4, 1, 14, 2, 13, 6, 10, 8, 5]
]


def generate_round_keys(key: bytes) -> List[int]:
    """Генерирует 32 раундовых ключа из 256-битного ключа."""
    if len(key) != 32:
        raise ValueError("Ключ должен быть 32 байта (256 бит)")
    
    # Разделяем ключ на 8-байтовые части и генерируем ключи
    round_keys = [int.from_bytes(key[i:i+4], 'big') for i in range(0, 32, 4)]
    
    # Повторяем ключи в тройном порядке и добавляем обратный порядок
    return round_keys * 3 + round_keys[::-1]


def G(a: int, k: int) -> int:
    """Преобразование G для сети Фейстеля."""
    t = (a + k) % (2 ** 32)
    t = ((t << 11) | (t >> 21)) & 0xFFFFFFFF  # Сдвиги
    result = 0
    # Применяем S-box
    for i in range(8):
        nibble = (t >> (4 * i)) & 0xF
        result |= SBOX[i][nibble] << (4 * i)
    return result


def encrypt_block(block: bytes, round_keys: List[int]) -> bytes:
    """Шифрует один 64-битный блок данных с использованием Магмы."""
    if len(block) != 8:
        raise ValueError("Блок должен быть длиной 8 байт")
    
    L = int.from_bytes(block[:4], 'big')
    R = int.from_bytes(block[4:], 'big')

    # 32 раунда с ключами
    for i in range(32):
        L, R = R, L ^ G(R, round_keys[i])

    return R.to_bytes(4, 'big') + L.to_bytes(4, 'big')


def decrypt_block(block: bytes, round_keys: List[int]) -> bytes:
    """Расшифровка одного 64-битного блока с использованием Магмы."""
    if len(block) != 8:
        raise ValueError("Блок должен быть длиной 8 байт")
    
    L = int.from_bytes(block[:4], 'big')
    R = int.from_bytes(block[4:], 'big')

    # 32 раунда в обратном порядке
    for i in range(31, -1, -1):
        L, R = R, L ^ G(R, round_keys[i])

    return R.to_bytes(4, 'big') + L.to_bytes(4, 'big')


def process_file(input_file: str, output_file: str, key: bytes, mode: str) -> None:
    """Обрабатывает файл: шифрует или расшифровывает его поблочно."""
    round_keys = generate_round_keys(key)
    
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        while block := f_in.read(8):
            if len(block) < 8:
                block += b'\x00' * (8 - len(block))

            result = encrypt_block(block, round_keys) if mode == "encrypt" else decrypt_block(block, round_keys)
            f_out.write(result)


def print_help() -> None:
    """Выводит справочную информацию по использованию программы."""
    print("Использование: python3 script.py [параметры]")
    print("Параметры:")
    print("  -h                Показать справку")
    print("\nИнтерактивный режим:")
    print("1. Запустите программу без параметров")
    print("2. Выберите режим (encrypt/decrypt), укажите файлы и введите ключ (256 бит hex)")


def main() -> None:
    """Основная функция программы для работы с параметрами и файлами."""
    if len(sys.argv) > 1 and sys.argv[1] == "-h":
        print_help()
        sys.exit(0)

    print("Шифрование/Расшифровка с использованием шифра Магма")
    
    # Режим работы
    mode = input("Выберите режим (encrypt/decrypt): ").strip().lower()
    while mode not in ["encrypt", "decrypt"]:
        print("Ошибка: введите 'encrypt' или 'decrypt'")
        mode = input("Выберите режим (encrypt/decrypt): ").strip().lower()

    # Ввод файлов
    input_file = input("Введите путь к входному файлу: ").strip()
    while not os.path.exists(input_file):
        print("Ошибка: файл не найден")
        input_file = input("Введите путь к входному файлу: ").strip()

    output_file = input("Введите путь к выходному файлу: ").strip()

    # Ввод ключа
    while True:
        key_hex = input("Введите ключ (256 бит в hex, 64 символа): ").strip()
        try:
            key = bytes.fromhex(key_hex)
            if len(key) == 32:
                break
            print("Ошибка: ключ должен быть 256 бит (64 символа в hex)")
        except ValueError:
            print("Ошибка: неверный формат hex-строки")

    # Обработка файла
    try:
        process_file(input_file, output_file, key, mode)
        print(f"Операция завершена! Результат сохранён в {output_file}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
