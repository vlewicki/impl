from functools import partial
from typing import Any, Callable
import dearcygui as dcg
from .modal_window import ModalWindow
from .keygen_window import KeydecryptWindow, KeygenWindow
from .. import crypto
import rsa

def read_first_file_as_bytes(paths: str, callback: Callable[[bytes, str], Any]):
    path = paths[0]
    if path:
        with open(path, 'rb') as f:
            callback(f.read(), path)


def write_file_as_bytes(path: str, bytes: bytes):
    with open(path, 'wb') as f:
        f.write(bytes)


def load_file(sender: dcg.uiItem, app_data, user_data, *, callback: Callable[[bytes, str], Any], title):
    dcg.os.show_open_file_dialog(sender.context, callback=partial(read_first_file_as_bytes, callback=callback), title=title, filters=[])


def save_file(sender: dcg.uiItem, app_data, user_data, *, callback: Callable[[list[str]], Any], title):
    dcg.os.show_save_file_dialog(sender.context, callback=callback, title=title, filters=[])


class MainWindow(dcg.Window):
    def __init__(self, context: dcg.Context, **kwargs):
        super().__init__(context, **kwargs)
        self._message: None | bytes = None
        self._private_key: None | rsa.PrivateKey = None
        self._public_key: None | rsa.PublicKey = None
        self._passphrase: None | str = None
        self._signature: None | bytes = None

        load_private_key = partial(load_file, callback=self._on_private_key_load, title="Select private key")
        load_public_key = partial(load_file, callback=self._on_public_key_load, title="Select public key")
        load_signature_file = partial(load_file, callback=self._on_signature_file_load, title="Select signature file")
        load_message_file = partial(load_file, callback=self._on_message_file_load, title="Select message file")

        save_private_key = partial(save_file, callback=self._on_private_key_save, title="Save private key")
        save_public_key = partial(save_file, callback=self._on_public_key_save, title="Save public key")
        save_signature = partial(save_file, callback=self._on_signature_save, title="Save signature")

        with self:
            with dcg.MenuBar(context):
                with dcg.Menu(context, label="File"):
                    dcg.MenuItem(context, label="Load message file", callback=load_message_file)
                    dcg.MenuItem(context, label="Load private key", callback=load_private_key)
                    dcg.MenuItem(context, label="Load public key", callback=load_public_key)
                    dcg.MenuItem(context, label="Load signature file", callback=load_signature_file)
                    dcg.Separator(context)
                    dcg.MenuItem(context, label="Save private key", callback=save_private_key)
                    dcg.MenuItem(context, label="Save public key", callback=save_public_key)
                    dcg.MenuItem(context, label="Save signature file", callback=save_signature)

                with dcg.Menu(context, label="Keys"):
                    dcg.MenuItem(context, label="Generate RSA key pair", callback=lambda: KeygenWindow(context, self._generate_rsa_key_pair))
                    # dcg.MenuItem(context, label="Set key passphrase")

                with dcg.Menu(context, label="Signature"):
                    dcg.MenuItem(context, label="Create signature", callback=self._on_signature_create)
                    dcg.MenuItem(context, label="Verify signature", callback=self._on_signature_verify)

                with dcg.Menu(context, label="Help"):
                    dcg.MenuItem(context, label="About", callback=lambda: ModalWindow(context, text="Выполнил: Левицкий В. Д.\nГруппа: А-13-22"))


            with dcg.VerticalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                with dcg.HorizontalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                    with dcg.VerticalLayout(context):
                        dcg.Text(context, value="Message:")
                        dcg.Text(context, value="Private key:")
                        dcg.Text(context, value="Public key:")
                        dcg.Text(context, value="Signature:")

                    with dcg.VerticalLayout(context):
                        self._message_indicator = dcg.Text(context, value="<Not loaded>")
                        self._private_key_indicator = dcg.Text(context, value="<Not loaded>")
                        self._public_key_indicator = dcg.Text(context, value="<Not loaded>")
                        self._signature_indicator = dcg.Text(context, value="<Not loaded>")

                with dcg.HorizontalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                    dcg.Button(context, label="Sign", callback=self._on_signature_create)
                    dcg.Button(context, label="Verify", callback=self._on_signature_verify)

    def _generate_rsa_key_pair(self, pub, priv, passphrase):
        self._public_key_indicator.value = "<Generated>"
        self._public_key_indicator.color = (0, 200, 0)
        self._private_key_indicator.value = "<Generated>"
        self._private_key_indicator.color = (0, 200, 0)
        self._public_key = pub
        self._private_key = priv
        self._passphrase = passphrase

    def _on_message_file_load(self, data: bytes, indicator_text: str):
        self._message = data
        self._message_indicator.value = indicator_text
        self._message_indicator.color = (0, 0, 0)

    def _on_private_key_load(self, data: bytes, indicator_text: str, passphrase=None):
        try:
            self._private_key = rsa.PrivateKey.load_pkcs1(data)
        except:
            KeydecryptWindow(self.context, data, partial(self._on_private_key_load, indicator_text=indicator_text))
        else:
            self._passphrase = passphrase
            self._private_key_indicator.value = indicator_text
            self._private_key_indicator.color = (0, 0, 0)

    def _on_public_key_load(self, data: bytes, indicator_text: str):
        self._public_key = rsa.PublicKey.load_pkcs1(data)
        self._public_key_indicator.value = indicator_text
        self._public_key_indicator.color = (0, 0, 0)

    def _on_signature_file_load(self, data: bytes, indicator_text: str):
        self._signature = data
        self._signature_indicator.value = indicator_text
        self._signature_indicator.color = (0, 0, 0)

    def _on_signature_create(self):
        if self._message is None:
            ModalWindow(self.context, "No message loaded")
            return
        if self._private_key is None:
            ModalWindow(self.context, "No private key loaded")
            return

        signature = crypto.sign_message(self._message, self._private_key)
        self._signature = signature
        self._signature_indicator.value = "<Signature created>"

        ModalWindow(self.context, "Signature created")

    def _on_signature_verify(self):
        if self._message is None:
            ModalWindow(self.context, "No message loaded")
            return
        if self._public_key is None:
            ModalWindow(self.context, "No public key loaded")
            return
        if self._signature is None:
            ModalWindow(self.context, "No signature loaded")
            return

        if crypto.verify_signature(self._message, self._signature, self._public_key):
            ModalWindow(self.context, "Signature verified")
        else:
            ModalWindow(self.context, "Signature verification failed")

    def _on_private_key_save(self, paths: list[str]):
        if self._private_key is None:
            ModalWindow(self.context, "No private key loaded")
            return
        if self._passphrase:
            chiphertext = crypto.encrypt_private_key(self._private_key, self._passphrase)
        else:
            chiphertext = self._private_key.save_pkcs1()
        write_file_as_bytes(paths[0], chiphertext)

    def _on_public_key_save(self, paths: list[str]):
        if self._public_key is None:
            ModalWindow(self.context, "No public key loaded")
            return

        write_file_as_bytes(paths[0], self._public_key.save_pkcs1())

    def _on_signature_save(self, paths: list[str]):
        if self._signature is None:
            ModalWindow(self.context, "No signature loaded")
            return

        write_file_as_bytes(paths[0], self._signature)
