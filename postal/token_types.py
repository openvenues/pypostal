from postal._token_types import *
from postal.utils.enum import Enum, EnumValue


class token_types(Enum):
    # Word types
    WORD = EnumValue(TOKEN_TYPE_WORD)
    ABBREVIATION = EnumValue(TOKEN_TYPE_ABBREVIATION)
    IDEOGRAPHIC_CHAR = EnumValue(TOKEN_TYPE_IDEOGRAPHIC_CHAR)
    HANGUL_SYLLABLE = EnumValue(TOKEN_TYPE_HANGUL_SYLLABLE)
    ACRONYM = EnumValue(TOKEN_TYPE_ACRONYM)

    # Special tokens
    EMAIL = EnumValue(TOKEN_TYPE_EMAIL)
    URL = EnumValue(TOKEN_TYPE_URL)
    US_PHONE = EnumValue(TOKEN_TYPE_US_PHONE)
    INTL_PHONE = EnumValue(TOKEN_TYPE_INTL_PHONE)

    # Numbers and numeric types
    NUMERIC = EnumValue(TOKEN_TYPE_NUMERIC)
    ORDINAL = EnumValue(TOKEN_TYPE_ORDINAL)
    ROMAN_NUMERAL = EnumValue(TOKEN_TYPE_ROMAN_NUMERAL)
    IDEOGRAPHIC_NUMBER = EnumValue(TOKEN_TYPE_IDEOGRAPHIC_NUMBER)

    # Punctuation types, may separate a phrase
    PERIOD = EnumValue(TOKEN_TYPE_PERIOD)
    EXCLAMATION = EnumValue(TOKEN_TYPE_EXCLAMATION)
    QUESTION_MARK = EnumValue(TOKEN_TYPE_QUESTION_MARK)
    COMMA = EnumValue(TOKEN_TYPE_COMMA)
    COLON = EnumValue(TOKEN_TYPE_COLON)
    SEMICOLON = EnumValue(TOKEN_TYPE_SEMICOLON)
    PLUS = EnumValue(TOKEN_TYPE_PLUS)
    AMPERSAND = EnumValue(TOKEN_TYPE_AMPERSAND)
    AT_SIGN = EnumValue(TOKEN_TYPE_AT_SIGN)
    POUND = EnumValue(TOKEN_TYPE_POUND)
    ELLIPSIS = EnumValue(TOKEN_TYPE_ELLIPSIS)
    DASH = EnumValue(TOKEN_TYPE_DASH)
    BREAKING_DASH = EnumValue(TOKEN_TYPE_BREAKING_DASH)
    HYPHEN = EnumValue(TOKEN_TYPE_HYPHEN)
    PUNCT_OPEN = EnumValue(TOKEN_TYPE_PUNCT_OPEN)
    PUNCT_CLOSE = EnumValue(TOKEN_TYPE_PUNCT_CLOSE)
    DOUBLE_QUOTE = EnumValue(TOKEN_TYPE_DOUBLE_QUOTE)
    SINGLE_QUOTE = EnumValue(TOKEN_TYPE_SINGLE_QUOTE)
    OPEN_QUOTE = EnumValue(TOKEN_TYPE_OPEN_QUOTE)
    CLOSE_QUOTE = EnumValue(TOKEN_TYPE_CLOSE_QUOTE)
    SLASH = EnumValue(TOKEN_TYPE_SLASH)
    BACKSLASH = EnumValue(TOKEN_TYPE_BACKSLASH)
    GREATER_THAN = EnumValue(TOKEN_TYPE_GREATER_THAN)
    LESS_THAN = EnumValue(TOKEN_TYPE_LESS_THAN)

    # Non-letters and whitespace
    OTHER = EnumValue(TOKEN_TYPE_OTHER)
    WHITESPACE = EnumValue(TOKEN_TYPE_WHITESPACE)
    NEWLINE = EnumValue(TOKEN_TYPE_NEWLINE)

    # Phrase, special application-level type not returned by the tokenizer
    PHRASE = 9999

    WORD_TOKEN_TYPES = set([
        WORD,
        ABBREVIATION,
        IDEOGRAPHIC_CHAR,
        HANGUL_SYLLABLE,
        ACRONYM
    ])

    NUMERIC_TOKEN_TYPES = set([
        NUMERIC,
        ORDINAL,
        ROMAN_NUMERAL,
        IDEOGRAPHIC_NUMBER,
    ])

    PUNCTUATION_TOKEN_TYPES = set([
        PERIOD,
        EXCLAMATION,
        QUESTION_MARK,
        COMMA,
        COLON,
        SEMICOLON,
        PLUS,
        AMPERSAND,
        AT_SIGN,
        POUND,
        ELLIPSIS,
        DASH,
        BREAKING_DASH,
        HYPHEN,
        PUNCT_OPEN,
        PUNCT_CLOSE,
        DOUBLE_QUOTE,
        SINGLE_QUOTE,
        OPEN_QUOTE,
        CLOSE_QUOTE,
        SLASH,
        BACKSLASH,
        GREATER_THAN,
        LESS_THAN,
    ])

    NON_ALPHANUMERIC_TOKEN_TYPES = PUNCTUATION_TOKEN_TYPES | set([
        OTHER,
        WHITESPACE,
        NEWLINE,
    ])
