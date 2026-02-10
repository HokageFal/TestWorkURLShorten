import pytest
from src.services.shortener import URLShortenerService, encode_base62, generate_short_code, BASE62_ALPHABET


def test_encode_base62_zero():
    assert encode_base62(0) == "0"


def test_encode_base62_small_numbers():
    assert encode_base62(10) == "a"
    assert encode_base62(35) == "z"
    assert encode_base62(36) == "A"
    assert encode_base62(61) == "Z"


def test_generate_short_code_deterministic():
    url = "https://example.com"
    code1 = generate_short_code(url)
    code2 = generate_short_code(url)
    assert code1 == code2


def test_generate_short_code_length():
    url = "https://example.com"
    code = generate_short_code(url, length=8)
    assert len(code) == 8


def test_create_short_url(in_memory_db):
    service = URLShortenerService(in_memory_db)
    url = "https://example.com"
    code = service.create_short_url(url)
    
    assert len(code) == 6
    assert all(c in BASE62_ALPHABET for c in code)


def test_create_short_url_with_custom_code(in_memory_db):
    service = URLShortenerService(in_memory_db)
    url = "https://example.com"
    custom_code = "mycode"
    
    code = service.create_short_url(url, custom_code=custom_code)
    assert code == custom_code


def test_custom_code_already_exists(in_memory_db):
    service = URLShortenerService(in_memory_db)
    url1 = "https://example.com"
    url2 = "https://another.com"
    custom_code = "mycode"
    
    service.create_short_url(url1, custom_code=custom_code)
    
    with pytest.raises(ValueError, match="уже занят"):
        service.create_short_url(url2, custom_code=custom_code)


def test_get_original_url(in_memory_db):
    service = URLShortenerService(in_memory_db)
    url = "https://example.com"
    code = service.create_short_url(url)
    
    retrieved_url = service.get_original_url(code)
    assert retrieved_url == url


def test_get_nonexistent_url(in_memory_db):
    service = URLShortenerService(in_memory_db)
    retrieved_url = service.get_original_url("nonexistent")
    assert retrieved_url is None


def test_delete_url(in_memory_db):
    service = URLShortenerService(in_memory_db)
    url = "https://example.com"
    code = service.create_short_url(url)
    
    deleted = service.delete_url(code)
    assert deleted is True
    
    retrieved_url = service.get_original_url(code)
    assert retrieved_url is None


def test_delete_nonexistent_url(in_memory_db):
    service = URLShortenerService(in_memory_db)
    deleted = service.delete_url("nonexistent")
    assert deleted is False


def test_get_url_stats(in_memory_db):
    service = URLShortenerService(in_memory_db)
    url = "https://example.com"
    code = service.create_short_url(url)
    
    stats = service.get_url_stats(code)
    assert stats is not None
    assert stats["original_url"] == url
    assert stats["short_code"] == code
    assert "created_at" in stats
    assert "id" in stats
