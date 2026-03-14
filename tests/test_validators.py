# =============================================================================
# ТЕСТЫ REALITY ВАЛИДАТОРОВ
# =============================================================================

import pytest
from src.core.validators import (
    validate_reality_public_key,
    validate_reality_short_id,
    validate_reality_fingerprint
)


class TestValidateRealityPublicKey:
    """Тесты валидации PUBLIC ключа REALITY"""

    def test_valid_public_key(self):
        """Валидный X25519 ключ"""
        # Реальный ключ (32 байта в base64 = 44 символа)
        # Пример валидного base64 ключа длиной 44 символа
        key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="  # 32 байта в base64
        assert validate_reality_public_key(key) is True

    def test_invalid_public_key_too_short(self):
        """Слишком короткий ключ"""
        key = "short"
        assert validate_reality_public_key(key) is False

    def test_invalid_public_key_not_base64(self):
        """Не base64"""
        key = "!!!invalid!!!"
        assert validate_reality_public_key(key) is False

    def test_empty_public_key(self):
        """Пустой ключ"""
        assert validate_reality_public_key("") is False

    def test_none_public_key(self):
        """None вместо ключа"""
        assert validate_reality_public_key(None) is False

    def test_public_key_wrong_size(self):
        """Ключ неправильного размера (не 32 байта)"""
        # 16 байт в base64
        key = "AAAAAAAAAAAAAAAAAAAAAA=="
        assert validate_reality_public_key(key) is False


class TestValidateRealityShortId:
    """Тесты валидации ShortId"""

    def test_empty_short_id(self):
        """Пустой ShortId допустим"""
        assert validate_reality_short_id("") is True

    def test_valid_short_id_8_bytes(self):
        """8 байт в hex (16 символов)"""
        assert validate_reality_short_id("1234567890abcdef") is True

    def test_valid_short_id_4_bytes(self):
        """4 байта в hex (8 символов)"""
        assert validate_reality_short_id("12345678") is True

    def test_valid_short_id_1_byte(self):
        """1 байт в hex (2 символа)"""
        assert validate_reality_short_id("ab") is True

    def test_invalid_short_id_too_long(self):
        """Слишком длинный (>8 байт)"""
        assert validate_reality_short_id("1234567890abcdef12") is False

    def test_invalid_short_id_not_hex(self):
        """Не hex символы"""
        assert validate_reality_short_id("ghijklmnop") is False

    def test_invalid_short_id_mixed_case(self):
        """Mixed case hex (допустимо)"""
        assert validate_reality_short_id("1234567890ABCDEF") is True

    def test_none_short_id(self):
        """None вместо ShortId"""
        assert validate_reality_short_id(None) is False


class TestValidateRealityFingerprint:
    """Тесты валидации fingerprint"""

    def test_valid_chrome(self):
        assert validate_reality_fingerprint("chrome") is True

    def test_valid_firefox(self):
        assert validate_reality_fingerprint("firefox") is True

    def test_valid_safari(self):
        assert validate_reality_fingerprint("safari") is True

    def test_valid_ios(self):
        assert validate_reality_fingerprint("ios") is True

    def test_valid_android(self):
        assert validate_reality_fingerprint("android") is True

    def test_valid_edge(self):
        assert validate_reality_fingerprint("edge") is True

    def test_valid_qq(self):
        assert validate_reality_fingerprint("qq") is True

    def test_valid_random(self):
        assert validate_reality_fingerprint("random") is True

    def test_valid_randomized(self):
        assert validate_reality_fingerprint("randomized") is True

    def test_valid_empty(self):
        assert validate_reality_fingerprint("") is True

    def test_valid_uppercase(self):
        """Fingerprint в верхнем регистре (допустимо)"""
        assert validate_reality_fingerprint("CHROME") is True

    def test_valid_mixed_case(self):
        """Fingerprint в смешанном регистре (допустимо)"""
        assert validate_reality_fingerprint("Chrome") is True

    def test_invalid_fingerprint(self):
        assert validate_reality_fingerprint("invalid") is False

    def test_invalid_fingerprint_typo(self):
        assert validate_reality_fingerprint("chrom") is False

    def test_none_fingerprint(self):
        """None вместо fingerprint"""
        assert validate_reality_fingerprint(None) is False
