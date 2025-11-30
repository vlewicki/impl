import random
import pytest
from app import crypto

key_lengths = [512, 1024, 2048]
message_lengths = list(range(1, 128, 4))

@pytest.fixture(scope="function")
def keys():
    return crypto.generate_keys(1024)

@pytest.mark.parametrize("message_len", message_lengths, ids=lambda x: f"length_{x}")
def test_crypto(message_len, keys):
    pub, priv = keys
    message = random.randbytes(message_len)
    signature = crypto.sign_message(message, priv)
    assert crypto.verify_signature(message, signature, pub)

@pytest.mark.parametrize("message_len", message_lengths, ids=lambda x: f"length_{x}")
def test_invalid(message_len, keys):
    pub, priv = keys
    message = random.randbytes(message_len)
    signature = crypto.sign_message(message, priv)
    assert not crypto.verify_signature(b'2'*message_len, signature, pub)
