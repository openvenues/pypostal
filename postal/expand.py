import _expand
from postal.utils.encoding import safe_decode


def expand_address(address, languages=None, **kw):
    '''
    @param address: the address as either Unicode or a UTF-8 encoded string
    @param languages: a tuple or list of ISO language code strings (e.g. "en", "fr", "de", etc.)
                      to use in expansion.

    '''
    address = safe_decode(address, 'utf-8')
    return _expand.expand_address(address, languages=languages, **kw)
