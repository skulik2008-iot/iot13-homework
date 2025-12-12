import os
import logging
import xml.etree.ElementTree as ET
from functools import wraps

class FileNotFound(Exception):
    pass

class FileCorrupted(Exception):
    pass



def logged(exception_type, mode="console"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)
            logger.setLevel(logging.INFO)
            if logger.hasHandlers():
                logger.handlers.clear()

            if mode == "console":
                handler = logging.StreamHandler()
            elif mode == "file":
                handler = logging.FileHandler("xml_log.txt", encoding="utf-8")
            else:
                raise ValueError("Невідомий режим логування")

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

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

    @logged(FileCorrupted, mode="console")
    def read(self):
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            return {child.tag: child.text for child in root}
        except Exception as e:
            raise FileCorrupted(f"Файл пошкоджено: {self.file_path} ({e})")

    @logged(FileCorrupted, mode="console")
    def write(self, data: dict):
        root = ET.Element("store")
        for key, value in data.items():
            el = ET.SubElement(root, key)
            el.text = str(value)
        tree = ET.ElementTree(root)
        tree.write(self.file_path, encoding="utf-8", xml_declaration=True)
        print("Дані записано")
        print(" Записані дані:", data)

    @logged(FileCorrupted, mode="console")
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



print(" Тест 1: Неіснуючий файл ")
try:
    handler = XMLHandler("nonexistent.xml")
except FileNotFound as e:
    print("Спіймано виняток:", e)

print("\n Тест 2: Створення обробника ")
test_file = "store_data.xml"
if not os.path.exists(test_file):
    root = ET.Element("store")
    ET.SubElement(root, "initial").text = "new"
    ET.SubElement(root, "status").text = "opened"
    ET.ElementTree(root).write(test_file, encoding="utf-8", xml_declaration=True)
print("Обробник створено для файлу:", test_file)

handler = XMLHandler(test_file)

print("\n Тест 3: Читання файлу ")
data = handler.read()
print("Прочитано дані:", data)

print("\n Тест 4: Запис у файл ")
new_data = {
    "store_name": "TechMarket",
    "location": "Львів",
    "owner": "Марія Сидоренко",
    "products": "Ноутбуки, Смартфони, Аксесуари",
    "sales": 150
}
handler.write(new_data)

print("\n Тест 5: Дописування у файл ")
extra_data = {
    "new_product": "Ігрова консоль",
    "monthly_profit": "25000 USD"
}
handler.append(extra_data)
final = handler.read()
print("  Фінальні дані:", final)

print("\n Тест 6: Пошкоджений XML файл ")
with open("corrupted.xml", "w", encoding="utf-8") as f:
    f.write("<store><broken><data>")  

try:
    broken_handler = XMLHandler("corrupted.xml")
    broken_handler.read()
except FileCorrupted as e:
    print("Спіймано виняток:", e)
