import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 310_000
MIN_ITERATIONS = 100_000
MAX_ITERATIONS = 2_000_000
SALT_BYTES = 16
DIGEST_BYTES = 32


def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("La contraseña no puede estar vacía.")
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS, dklen=DIGEST_BYTES)
    return ALGORITHM + "$" + str(ITERATIONS) + "$" + salt.hex() + "$" + digest.hex()


def verify_password(password: str, stored_hash: str) -> tuple[bool, bool]:
    if not isinstance(password, str) or not isinstance(stored_hash, str):
        return False, False
    if stored_hash.startswith(ALGORITHM + "$"):
        try:
            algorithm, raw_iterations, salt_hex, digest_hex = stored_hash.split("$")
            iterations = int(raw_iterations)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            if algorithm != ALGORITHM or not MIN_ITERATIONS <= iterations <= MAX_ITERATIONS:
                return False, False
            if not 16 <= len(salt) <= 64 or len(expected) != DIGEST_BYTES:
                return False, False
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=DIGEST_BYTES)
            valid = hmac.compare_digest(actual, expected)
            return valid, valid and iterations < ITERATIONS
        except (ValueError, TypeError, OverflowError):
            return False, False
    if len(stored_hash) != 64:
        return False, False
    try:
        expected = bytes.fromhex(stored_hash)
    except ValueError:
        return False, False
    valid = hmac.compare_digest(hashlib.sha256(password.encode("utf-8")).digest(), expected)
    return valid, valid
