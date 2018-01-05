"""Python bindings to libpostal near_dupe_hashes."""

from postal import _dedupe
from postal.utils.enum import Enum, EnumValue


class duplicate_status(Enum):
    NULL_DUPLICATE = EnumValue(_dedupe.NULL_DUPLICATE_STATUS)
    NON_DUPLICATE = EnumValue(_dedupe.NON_DUPLICATE)
    NEEDS_REVIEW = EnumValue(_dedupe.POSSIBLE_DUPLICATE_NEEDS_REVIEW)
    LIKELY_DUPLICATE = EnumValue(_dedupe.LIKELY_DUPLICATE)
    EXACT_DUPLICATE = EnumValue(_dedupe.EXACT_DUPLICATE)


def place_languages(labels, values):
    return _dedupe.place_languages(labels, values)


def is_name_duplicate(value1, value2, languages=None):
    dupe_status = _dedupe.is_name_duplicate(value1, value2, languages=languages)
    return duplicate_status.from_id(dupe_status)


def is_street_duplicate(value1, value2, languages=None):
    dupe_status = _dedupe.is_street_duplicate(value1, value2, languages=languages)
    return duplicate_status.from_id(dupe_status)


def is_house_number_duplicate(value1, value2, languages=None):
    dupe_status = _dedupe.is_house_number_duplicate(value1, value2, languages=languages)
    return duplicate_status.from_id(dupe_status)


def is_po_box_duplicate(value1, value2, languages=None):
    dupe_status = _dedupe.is_po_box_duplicate(value1, value2, languages=languages)
    return duplicate_status.from_id(dupe_status)


def is_unit_duplicate(value1, value2, languages=None):
    dupe_status = _dedupe.is_unit_duplicate(value1, value2, languages=languages)
    return duplicate_status.from_id(dupe_status)


def is_floor_duplicate(value1, value2, languages=None):
    dupe_status = _dedupe.is_floor_duplicate(value1, value2, languages=languages)
    return duplicate_status.from_id(dupe_status)


def is_postal_code_duplicate(value1, value2, languages=None):
    dupe_status = _dedupe.is_postal_code_duplicate(value1, value2, languages=languages)
    return duplicate_status.from_id(dupe_status)


def is_toponym_duplicate(labels1, values1, labels2, values2, languages=None):
    dupe_status = _dedupe.is_toponym_duplicate(labels1, values1, labels2, values2, languages=languages)
    return duplicate_status.from_id(dupe_status)


def is_name_duplicate_fuzzy(tokens1, scores1, tokens2, scores2, languages=None, **kw):
    dupe_status, sim = _dedupe.is_name_duplicate_fuzzy(tokens1, scores1, tokens2, scores2, languages=languages, **kw)
    return duplicate_status.from_id(dupe_status), sim


def is_street_duplicate_fuzzy(tokens1, scores1, tokens2, scores2, languages=None, **kw):
    dupe_status, sim = _dedupe.is_street_duplicate_fuzzy(tokens1, scores1, tokens2, scores2, languages=languages, **kw)
    return duplicate_status.from_id(dupe_status), sim
