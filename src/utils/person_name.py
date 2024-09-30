import re


def valid_name(name: str) -> bool:
    if len(name) <= 1:
        return False
    if not re.fullmatch('[а-яА-Я]+', name):
        return False
    return True


def format_person_name(name: str) -> str:
    name_parts = name.split()
    formatted_parts = [part.capitalize().replace("ё", "е").replace('Ё', 'Е') for part in name_parts]
    return ' '.join(formatted_parts)

