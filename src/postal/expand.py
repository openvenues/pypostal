# -*- coding: utf-8 -*-
"""Python bindings to libpostal expand_address."""

from __future__ import unicode_literals
from postal import _expand
from postal.utils.encoding import safe_decode


def expand_address(address, languages=None, **kw):
    """
    Expand the given address into one or more normalized strings.

    Required
    --------
    @param address: the address as either Unicode or a UTF-8 encoded string

    Options
    -------
    @param languages: a tuple or list of ISO language code strings (e.g. "en", "fr", "de", etc.)
                      to use in expansion. If None is passed, use language classifier
                      to detect language automatically.
    @param address_components: an integer (bit-set) of address component expansions
                               to use e.g. ADDRESS_NAME | ADDRESS_STREET would use
                               only expansions which apply to venue names or streets.
    @param latin_ascii: use the Latin to ASCII transliterator, which normalizes e.g. æ => ae
    @param transliterate: use any available transliterators for non-Latin scripts, e.g.
                          for the Greek phrase διαφορετικούς becomes diaphoretikoús̱
    @param strip_accents: strip accented characters e.g. é => e, ç => c. This loses some
                          information in various languags, but in general we want
    @param decompose: perform Unicode normalization (NFD form)
    @param lowercase: UTF-8 lowercase the string
    @param trim_string: trim spaces on either side of the string
    @param replace_word_hyphens: add version of the string replacing hyphens with space
    @param delete_word_hyphens: add version of the string with hyphens deleted
    @param replace_numeric_hyphens: add version of the string with numeric hyphens replaced 
                                    e.g. 12345-6789 => 12345 6789
    @param delete_numeric_hyphens: add version of the string with numeric hyphens removed
                                   e.g. 12345-6789 => 123456789
    @param split_alpha_from_numeric: split tokens like CR17 into CR 17, helps with expansion
                                     of certain types of highway abbreviations
    @param delete_final_periods: remove final periods on abbreviations e.g. St. => St
    @param delete_acronym_periods: remove periods in acronyms e.g. U.S.A. => USA
    @param drop_english_possessives: normalize possessives e.g. Mark's => Marks
    @param delete_apostrophes: delete other types of hyphens e.g. O'Malley => OMalley
    @param expand_numex: converts numeric expressions e.g. Twenty sixth => 26th,
                         using either the supplied languages or the result of
                         automated language classification.
    @param roman_numerals: normalize Roman numerals e.g. IX => 9. Since these can be
                           ambiguous (especially I and V), turning this on simply
                           adds another version of the string if any potential
                           Roman numerals are found.
    """
    address = safe_decode(address, 'utf-8')
    return _expand.expand_address(address, languages=languages, **kw)


def expand_address_root(address, languages=None, **kw):
    return expand_address(address, languages=languages, root=True, **kw)


# Constants for address components
ADDRESS_NONE = _expand.ADDRESS_NONE
ADDRESS_ANY = _expand.ADDRESS_ANY
ADDRESS_NAME = _expand.ADDRESS_NAME
ADDRESS_HOUSE_NUMBER = _expand.ADDRESS_HOUSE_NUMBER
ADDRESS_STREET = _expand.ADDRESS_STREET
ADDRESS_UNIT = _expand.ADDRESS_UNIT
ADDRESS_LEVEL = _expand.ADDRESS_LEVEL
ADDRESS_STAIRCASE = _expand.ADDRESS_STAIRCASE
ADDRESS_ENTRANCE = _expand.ADDRESS_ENTRANCE
ADDRESS_CATEGORY = _expand.ADDRESS_CATEGORY
ADDRESS_NEAR = _expand.ADDRESS_NEAR
ADDRESS_TOPONYM = _expand.ADDRESS_TOPONYM
ADDRESS_POSTAL_CODE = _expand.ADDRESS_POSTAL_CODE
ADDRESS_PO_BOX = _expand.ADDRESS_PO_BOX
ADDRESS_ALL = _expand.ADDRESS_ALL
