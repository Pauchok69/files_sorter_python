import shutil
import sys
import time
from pathlib import Path

# Словник з розширеннями для сортування
EXTENSIONS_DICT = {
    'images': ('.jpeg', '.png', '.jpg', '.svg', '.dng'),
    'video': ('.avi', '.mp4', '.mov', '.mkv'),
    'documents': ('.doc', '.docx', '.txt', '.pdf', '.xls', '.xlsx', '.pptx'),
    'audio': ('.mp3', '.ogg', '.wav', '.amr'),
    'archives': ('.zip', '.gz', '.tar')
}

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
trans = {}

# За замовчуванням - None. Потім приймає шлях
main_folder: Path | None = None


def main():
    """Перевіряємо дійсність і існування шляху указаного користувачем
        Повертаємо запуск наступної функції - cleaner.
        root_folder - так записуємо шлях до папки котру будемо чистити та сортувати.
    """
    global main_folder

    if len(sys.argv) < 2:
        print('Enter path to folder which should be cleaned')
        exit()

    root_folder = Path(sys.argv[1])
    # root_folder => Path("D:\Maya\Desktop\Хлам")

    if (not root_folder.exists()) or (not root_folder.is_dir()):
        print('Path incorrect')
        exit()

    main_folder = root_folder
    fill_translate()
    cleaner(root_folder)


def cleaner(folder: Path):
    """Приймає на вхід шлях до папки котру будемо перевіряти.
        Перевіряє всі входження в директорію - чи це файл чи директорія.
        І для директорій рекурсивно заходить в них та так само їх перевіряє.
    """
    for file in folder.iterdir():

        if file.is_file():
            # Будемо передавати цей файл далі на сортування і переміщення до нової папки.
            sort_file(file)

        if file.is_dir():
            # Будемо заходити всередину папки та повертати її вміст знову в середину цієї ж функції.
            # Надалі видаляти пусту папку.

            cleaner(file)

            # Видаляємо директорію, якщо вона порожня
            if not any(file.iterdir()):
                file.rmdir()


def sort_file(file: Path) -> None:
    file_suffix = file.suffix.lower()
    # Приберемо розширення(extension) з імені файлу
    file_name = file.stem

    # key => music, values => ['.mp3', '.ogg', '.wav', '.amr']
    for key, values in EXTENSIONS_DICT.items():
        if file_suffix in values:
            # Відправляємо ім'я файлу в функцію normalize() для нормалізації імені
            normalized_file_name = normalize(file_name)
            new_file_name = normalized_file_name + file_suffix
            # Переміщуємо в нову папку, яка відповідає ключу
            end_folder = main_folder.joinpath(key)

            # Створюємо папку по даному шляху якщо її не існує. end_folder (Приклад: D:\Maya\Desktop\Хлам\images)
            end_folder.mkdir(exist_ok=True)
            new_file_path = end_folder.joinpath(new_file_name)  # Приклад: D:\Maya\Desktop\Хлам\images\test.jpg

            try:
                move_file(file, new_file_path)
            except FileExistsError:
                timestamp = time.time()
                new_file_path = end_folder.joinpath(f"{normalized_file_name}_{str(timestamp)}{file_suffix}")

                move_file(file, new_file_path)

            if key == 'archives':
                # Шлях до папки з відкритим архівом
                base_archive_dir = end_folder.joinpath(normalized_file_name)  # Створюємо шлях
                base_archive_dir.mkdir(exist_ok=True)  # Створюємо папку
                # new_file_path => D:\Maya\Desktop\Хлам\archives\test.zip
                # base_archive_dir => D:\Maya\Desktop\Хлам\archives\test\...
                shutil.unpack_archive(new_file_path, base_archive_dir)


def move_file(file: Path, new_file_path: Path) -> None:
    file.rename(new_file_path)


def fill_translate():
    """
    Створює MAP для перекладу і заповнює змінну trans
    """
    for cyril, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        trans[ord(cyril)] = latin
        trans[ord(cyril.upper())] = latin.upper()


def normalize(file_name: str) -> str:
    """
    Замінює неліквідні знаки на "_" та кириличні букви на латинські
    :param file_name: Ім'я файлу без розширення та шляху
    :return: нормалізоване ім'я без розширення
    """
    normalized_name = file_name.translate(trans)

    for i in normalized_name:
        if not i.isdigit() and not i.isalpha() and i != '_':
            normalized_name = normalized_name.replace(i, '_')

    return normalized_name


if __name__ == '__main__':
    main()
    print("Finished!!!")
    exit()
