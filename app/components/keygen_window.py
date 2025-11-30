from typing import Callable
import dearcygui as dcg

from .modal_window import ModalWindow
from .. import crypto

class KeygenWindow(dcg.Window):
    def __init__(self, context: dcg.Context, on_generated_callback):
        width=400
        height=400
        self._on_generated_callback = on_generated_callback
        super().__init__(context, modal=True, no_move=True, autosize=True, no_title_bar=True, x="viewport.width / 2 - self.width / 2", y="viewport.height / 2 - self.height / 2")
        with self:
            with dcg.HorizontalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                with dcg.VerticalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                    self._key_length = dcg.InputValue(context, label="Key length (bits)", print_format="%.0f", step=1, value=1024, min_value=128, max_value=8192)
                    self._passphrase = dcg.InputText(context, label="Passphrase (optional)", password=True)
                    self._repeat_passphrase = dcg.InputText(context, label="Repeat passphrase", password=True)
                    dcg.Button(context, label="Generate", callback=self._on_generate)

    def _on_generate(self, button):
        if self._passphrase.value != self._repeat_passphrase.value:
            ModalWindow(self.context, "Passphrases do not match")
            return
        button.enabled = False
        button.label = "Generating..."
        pub, priv = crypto.generate_keys(int(self._key_length.value))
        self._on_generated_callback(pub, priv, self._passphrase.value)
        ModalWindow(self.context, "Key Pair Generated")
        self.delete_item()


class KeydecryptWindow(dcg.Window):
    def __init__(self, context: dcg.Context, encrypted_key, on_decrypted_callback):
        width=400
        height=400
        self._on_decrypted_callback = on_decrypted_callback
        self._encrypted_key = encrypted_key
        super().__init__(context, modal=True, no_move=True, autosize=True, no_title_bar=True, x="viewport.width / 2 - self.width / 2", y="viewport.height / 2 - self.height / 2")
        with self:
            self._passphrase = dcg.InputText(context, label="Passphrase", password=True)
            dcg.Button(context, label="Decrypt", callback=self._on_decrypt)

    def _on_decrypt(self, button):
        if self._passphrase.value == "":
            ModalWindow(self.context, "Passphrase cannot be empty")
            return
        button.enabled = False
        button.label = "Decrypting..."
        try:
            priv = crypto.decrypt_private_key(self._encrypted_key, self._passphrase.value)
        except ValueError:
            ModalWindow(self.context, "Invalid Passphrase")
        else:
            self._on_decrypted_callback(priv)
            ModalWindow(self.context, "Key Decrypted")
            self.delete_item()
