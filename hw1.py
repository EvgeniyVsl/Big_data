"""
Given a file containing text. Complete using only default collections:
    1) Find 10 longest words consisting from largest amount of unique symbols
    2) Find rarest symbol for document
    3) Count every punctuation char
    4) Count every non ascii char
    5) Find most common non ascii char for document
"""

from typing import List
from collections import Counter
from collections import defaultdict
import string

# Преобразуем символы в нужный формат перед выполнение любой операции
def decode_unicode_escape(text: str) -> str:
    return text.encode('latin-1').decode('unicode-escape')

def get_longest_diverse_words(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    text = decode_unicode_escape(text)
    words = text.split()
    unique_count = {word.strip(string.punctuation): len(set(word.strip(string.punctuation))) for word in words}
    sorted_words = sorted(unique_count.keys(), key=lambda w: (-len(w), -unique_count[w.strip(string.punctuation)]))
    return sorted_words[:10]

def get_rarest_char(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    text = decode_unicode_escape(text)
    char_count = Counter(text)
    return min(char_count, key=char_count.get)

def count_punctuation_chars(file_path: str) -> int:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    text = decode_unicode_escape(text)
    return sum(1 for char in text if char in string.punctuation)

def count_non_ascii_chars(file_path: str) -> defaultdict:
    non_ascii_counter = defaultdict(int)
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    text = decode_unicode_escape(text)
    for char in text:
        if ord(char) > 127:
            non_ascii_counter[char] += 1
    return dict(non_ascii_counter)

def get_most_common_non_ascii_char(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    text = decode_unicode_escape(text)
    non_ascii_chars = [char for char in text if ord(char) > 127]
    if not non_ascii_chars:
        return ''
    return Counter(non_ascii_chars).most_common(1)[0][0]


file_path = '11.03\задание с текстом\data.txt'
print('10 самых длинных слов с наибольшим количеством уникальных символов:')
print(get_longest_diverse_words(file_path))
print('Самый редкий символ в тексте:')
print(get_rarest_char(file_path))
print('Количество пунктуационных знаков:')
print(count_punctuation_chars(file_path))
print('Количество не ASCII символов:')
print(count_non_ascii_chars(file_path))
print('Наиболее частый не ASCII символ:')
print(get_most_common_non_ascii_char(file_path))