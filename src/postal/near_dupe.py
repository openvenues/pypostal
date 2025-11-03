"""Python bindings to libpostal near_dupe_hashes."""

from postal import _near_dupe


def name_hashes(name, languages=None, **kw):
    return _near_dupe.name_hashes(name, languages=languages, **kw)


def near_dupe_hashes(labels, values, languages=None, **kw):
    """
    Hash the given address into normalized strings that can be used to group similar
    addresses together for more detailed pairwise comparison. This can be thought of
    as the blocking function in record linkage or locally-sensitive hashing in the
    document near-duplicate detection.

    Required
    --------
    @param labels: array of component labels as either Unicode or UTF-8 encoded strings
                   e.g. ["house_number", "road", "postcode"]
    @param values: array of component values as either Unicode or UTF-8 encoded strings
                   e.g. ["123", "Broadway", "11216"]. Note len(values) must be equal to
                   len(labels).

    Options
    -------
    @param languages: a tuple or list of ISO language code strings (e.g. "en", "fr", "de", etc.)
                      to use in expansion. If None is passed, use language classifier
                      to detect language automatically.
    @param with_name: use name in the hashes
    @param with_address: use house_number & street in the hashes
    @param with_unit: use secondary unit as part of the hashes
    @param with_city_or_equivalent: use the city, city_district, suburb, or island name as one of
                                    the geo qualifiers
    @param with_small_containing_boundaries: use small containing boundaries (currently state_district)
                                             as one of the geo qualifiers
    @param with_postal_code: use postal code as one of the geo qualifiers
    @param with_latlon: use geohash + neighbors as one of the geo qualifiers
    @param latitude: latitude (Y coordinate)
    @param longitude: longitude (X coordinate)
    @param geohash_precision: geohash tile size (default = 6)
    @param name_and_address_keys: include keys with name + address + geo
    @param name_only_keys: include keys with name + geo
    @param address_only_keys: include keys with address + geo
    """
    return _near_dupe.near_dupe_hashes(labels, values, languages=languages, **kw)
