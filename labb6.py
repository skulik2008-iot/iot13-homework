import os
import logging
import xml.etree.ElementTree as ET
from functools import wraps


class FileNotFound(Exception):
    pass

class FileCorrupted(Exception):
    pass


logger = logging.getLogger("xml_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def logged(exception_type=Exception):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Виконання операції: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Операція {func.__name__} успішно завершена")
                return result
            except exception_type as e:
                logger.error(f"Виняток {exception_type.__name__}: {e}")
                raise
        return wrapper
    return decorator


class XMLHandler:
    def __init__(self, file_path):
        self.file_path = file_path

        if not os.path.exists(file_path):
            raise FileNotFound(f"Файл не знайдено: {file_path}")

        if not file_path.endswith(".xml"):
            raise FileCorrupted("Файл не є XML")


    @logged(FileCorrupted)
    def read(self):
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()

            result = {}
            for child in root:
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child.text)
                else:
                    result[child.tag] = child.text

            return result

        except Exception as e:
            raise FileCorrupted(f"Файл пошкоджено: {self.file_path} ({e})")


    @logged(FileCorrupted)
    def write(self, data: dict):
        try:
            root = ET.Element("store")
            for key, value in data.items():
                el = ET.SubElement(root, key)
                el.text = str(value)

            tree = ET.ElementTree(root)
            tree.write(self.file_path, encoding="utf-8", xml_declaration=True)

            print("Дані записано")
            print("Записані дані:", data)

        except Exception as e:
            raise FileCorrupted(f"Помилка запису у файл: {e}")


    @logged(FileCorrupted)
    def append(self, data: dict):
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()

            for key, value in data.items():
                el = ET.SubElement(root, key)
                el.text = str(value)

            tree.write(self.file_path, encoding="utf-8", xml_declaration=True)
            print("Дані дописано")

        except Exception as e:
            raise FileCorrupted(f"Файл пошкоджено: {self.file_path} ({e})")


def main():
    print("Тест 1: Неіснуючий файл")
    try:
        XMLHandler("nonexistent.xml")
    except FileNotFound as e:
        print("Спіймано виняток:", e)

    print("\nТест 2: Створення обробника")
    test_file = "store_data.xml"

    if not os.path.exists(test_file):
        root = ET.Element("store")
        ET.SubElement(root, "initial").text = "new"
        ET.SubElement(root, "status").text = "opened"
        ET.ElementTree(root).write(test_file, encoding="utf-8", xml_declaration=True)

    handler = XMLHandler(test_file)
    print("Обробник створено для файлу:", test_file)

    print("\nТест 3: Читання файлу")
    data = handler.read()
    print("Прочитано дані:", data)

    print("\nТест 4: Запис у файл")
    handler.write({
        "store_name": "TechMarket",
        "location": "Львів",
        "owner": "Марія Сидоренко",
        "sales": 150
    })

    print("\nТест 5: Дописування у файл")
    handler.append({
        "new_product": "Ігрова консоль",
        "monthly_profit": "25000 USD"
    })

    print("Фінальні дані:", handler.read())

    print("\nТест 6: Пошкоджений XML файл")
    with open("corrupted.xml", "w", encoding="utf-8") as f:
        f.write("<store><broken><data>")

    try:
        XMLHandler("corrupted.xml").read()
    except FileCorrupted as e:
        print("Спіймано виняток:", e)


if __name__ == "__main__":
    main()
