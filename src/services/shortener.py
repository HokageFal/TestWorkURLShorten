import hashlib
import random
import string
from typing import Optional

from src.database import Database
from src.cruds import links as links_crud

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase


def encode_base62(num: int) -> str:
    if num == 0:
        return BASE62_ALPHABET[0]
    
    result = []
    base = len(BASE62_ALPHABET)
    
    while num:
        num, remainder = divmod(num, base)
        result.append(BASE62_ALPHABET[remainder])
    
    return ''.join(reversed(result))


def generate_short_code(url: str, length: int = 6) -> str:
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    hash_int = int(url_hash[:8], 16)
    short_code = encode_base62(hash_int)
    
    if len(short_code) < length:
        short_code = short_code.ljust(length, BASE62_ALPHABET[0])
    else:
        short_code = short_code[:length]
    
    return short_code


def generate_random_code(length: int = 6) -> str:
    return ''.join(random.choices(BASE62_ALPHABET, k=length))


class URLShortenerService:
    def __init__(self, database: Database):
        self.db = database
    
    def create_short_url(self, original_url: str, custom_code: Optional[str] = None, max_attempts: int = 5) -> str:
        if custom_code:
            if links_crud.code_exists(self.db, custom_code):
                raise ValueError(f"Код '{custom_code}' уже занят")
            links_crud.create_link(self.db, original_url, custom_code)
            return custom_code
        
        short_code = generate_short_code(original_url)
        
        if not links_crud.code_exists(self.db, short_code):
            links_crud.create_link(self.db, original_url, short_code)
            return short_code
        
        for _ in range(max_attempts):
            short_code = generate_random_code()
            if not links_crud.code_exists(self.db, short_code):
                links_crud.create_link(self.db, original_url, short_code)
                return short_code
        
        raise RuntimeError(f"Не удалось создать уникальный код после {max_attempts} попыток")
    
    def get_original_url(self, short_code: str) -> Optional[str]:
        result = links_crud.get_link_by_code(self.db, short_code)
        return result["original_url"] if result else None
    
    def delete_url(self, short_code: str) -> bool:
        return links_crud.delete_link(self.db, short_code)
    
    def get_url_stats(self, short_code: str) -> Optional[dict]:
        return links_crud.get_stats(self.db, short_code)
