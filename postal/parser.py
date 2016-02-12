"""Python bindings to libpostal parse_address."""
from postal import _parser
from postal.utils.encoding import safe_decode


def parse_address(address, language=None, country=None):
    """
    Parse address into components.

    @param address: the address as either Unicode or a UTF-8 encoded string
    @param language (optional): language code
    @param country (optional): country code
    """
    address = safe_decode(address, 'utf-8')
    return _parser.parse_address(address, language=language, country=country)
