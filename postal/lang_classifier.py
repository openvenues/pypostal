"""Python bindings to libpostal parse_address."""
from postal import _langclassifier
from postal.utils.encoding import safe_decode


def classify_lang_address(address):
    """
    Classify the language of an address.

    @param address: the address as either Unicode or a UTF-8 encoded string
    """
    address = safe_decode(address, 'utf-8')
    return _langclassifier.classify_lang_address(address)
