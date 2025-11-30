import hashlib
import rsa
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

DECRYPTED_INDICATOR = b"indicator"


def generate_keys(length: int):
    return rsa.newkeys(length)

def hash_message(message: bytes) -> bytes:
    return hashlib.sha256(message).digest()

def key_from_passphrase(passphrase: str) -> bytes:
    return hashlib.sha256(passphrase.encode()).digest()

def encrypt_private_key(private_key: rsa.PrivateKey, passphrase: str) -> bytes:
    key = key_from_passphrase(passphrase)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(DECRYPTED_INDICATOR + private_key.save_pkcs1())
    return cipher.nonce + tag + ciphertext

def decrypt_private_key(ciphertext: bytes, passphrase: str) -> rsa.PrivateKey:
    key = key_from_passphrase(passphrase)
    cipher = AES.new(key, AES.MODE_EAX, ciphertext[:16])
    data = cipher.decrypt(ciphertext[16:])
    if data[:len(DECRYPTED_INDICATOR)] != DECRYPTED_INDICATOR:
        raise ValueError("Invalid decryption")
    private_key = rsa.PrivateKey.load_pkcs1(data[len(DECRYPTED_INDICATOR):])
    return private_key


def power(base: int, exponent: int, modulus: int) -> int:
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent //= 2
        base = (base * base) % modulus
    return result

def sign_message(message: bytes, private_key: rsa.PrivateKey) -> bytes:
    hash = hash_message(message)
    signature = power(int.from_bytes(hash, byteorder='big'), private_key.d, private_key.n)
    return signature.to_bytes((signature.bit_length() + 7) // 8, byteorder='big')

def verify_signature(message: bytes, signature: bytes, public_key: rsa.PublicKey) -> bool:
    signature_int = int.from_bytes(signature, byteorder='big')
    hash = int.from_bytes(hash_message(message), byteorder='big')
    return power(signature_int, public_key.e, public_key.n) == hash
