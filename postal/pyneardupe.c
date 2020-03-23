#include <Python.h>
#include <libpostal/libpostal.h>

#include "pyutils.h"

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

struct module_state {
    PyObject *error;
};


#ifdef IS_PY3K
    #define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
    #define GETSTATE(m) (&_state)
    static struct module_state _state;
#endif

static PyObject *py_near_dupe_hashes(PyObject *self, PyObject *args, PyObject *keywords) {
    PyObject *arg_labels;
    PyObject *arg_values;
    PyObject *arg_languages = Py_None;
    libpostal_near_dupe_hash_options_t options = libpostal_get_near_dupe_hash_default_options();

    PyObject *result = NULL;

    static char *kwlist[] = {"labels",
                             "values",
                             "languages", 
                             "with_name",
                             "with_address",
                             "with_unit",
                             "with_city_or_equivalent",
                             "with_small_containing_boundaries",
                             "with_postal_code",
                             "with_latlon",
                             "latitude",
                             "longitude",
                             "geohash_precision",
                             "name_and_address_keys",
                             "name_only_keys",
                             "address_only_keys",
                             NULL
                            };

    uint32_t with_name = options.with_name;
    uint32_t with_address = options.with_address;
    uint32_t with_unit = options.with_unit;
    uint32_t with_city_or_equivalent = options.with_city_or_equivalent;
    uint32_t with_small_containing_boundaries = options.with_small_containing_boundaries;
    uint32_t with_postal_code = options.with_postal_code;
    uint32_t with_latlon = options.with_latlon;
    double latitude = options.latitude;
    double longitude = options.longitude;
    uint32_t geohash_precision = options.geohash_precision;
    uint32_t name_and_address_keys = options.name_and_address_keys;
    uint32_t name_only_keys = options.name_only_keys;
    uint32_t address_only_keys = options.address_only_keys;

    if (!PyArg_ParseTupleAndKeywords(args, keywords, 
                                     "OO|OIIIIIIIddIIII:near_dupe", kwlist,
                                     &arg_labels,
                                     &arg_values,
                                     &arg_languages,
                                     &with_name,
                                     &with_address,
                                     &with_unit,
                                     &with_city_or_equivalent,
                                     &with_small_containing_boundaries,
                                     &with_postal_code,
                                     &with_latlon,
                                     &latitude,
                                     &longitude,
                                     &geohash_precision,
                                     &name_and_address_keys,
                                     &name_only_keys,
                                     &address_only_keys
                                     )) {
        return 0;
    }

    if (!PySequence_Check(arg_labels) || !PySequence_Check(arg_values)) {
        PyErr_SetString(PyExc_TypeError,
                        "Input labels and values must be sequences");
        return 0;
    } else if (PySequence_Length(arg_labels) != PySequence_Length(arg_values)) {
        PyErr_SetString(PyExc_TypeError,
                        "Input labels and values arrays must be of equal length");
        return 0;
    }

    options.with_name = with_name;
    options.with_address = with_address;
    options.with_unit = with_unit;
    options.with_city_or_equivalent = with_city_or_equivalent;
    options.with_small_containing_boundaries = with_small_containing_boundaries;
    options.with_postal_code = with_postal_code;
    options.with_latlon = with_latlon;
    options.latitude = latitude;
    options.longitude = longitude;
    options.geohash_precision = geohash_precision;
    options.name_and_address_keys = name_and_address_keys;
    options.name_only_keys = name_only_keys;
    options.address_only_keys = address_only_keys;

    size_t num_languages = 0;
    char **languages = NULL;

    if (PySequence_Check(arg_languages)) {
        languages = PyObject_to_strings_max_len(arg_languages, LIBPOSTAL_MAX_LANGUAGE_LEN, &num_languages);
    }

    size_t num_labels = 0;
    char **labels = PyObject_to_strings(arg_labels, &num_labels);

    if (labels == NULL) {
        goto exit_free_languages;
    }

    size_t num_values = 0;
    char **values = PyObject_to_strings(arg_values, &num_values);

    if (values == NULL) {
        goto exit_free_labels;
    }

    size_t num_hashes = 0;
    char **near_dupe_hashes = NULL;

    size_t num_components = num_labels;

    if (num_languages > 0 && languages != NULL) {
        near_dupe_hashes = libpostal_near_dupe_hashes_languages(num_components, labels, values, options, num_languages, languages, &num_hashes);
    } else {
        near_dupe_hashes = libpostal_near_dupe_hashes(num_components, labels, values, options, &num_hashes);
    }

    if (near_dupe_hashes != NULL) {
        result = PyObject_from_strings(near_dupe_hashes, num_hashes);
        string_array_destroy(near_dupe_hashes, num_hashes);
    } else {
        result = Py_None;
        Py_INCREF(Py_None);
    }

    string_array_destroy(values, num_values);

exit_free_labels:
    string_array_destroy(labels, num_labels);
exit_free_languages:
    string_array_destroy(languages, num_languages);

    return result;
}

static PyMethodDef near_dupe_methods[] = {
    {"near_dupe_hashes", (PyCFunction)py_near_dupe_hashes, METH_VARARGS | METH_KEYWORDS, "near_dupe_hashes(labels, values, **kw)"},
    {NULL, NULL},
};



#ifdef IS_PY3K

static int near_dupe_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int near_dupe_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    libpostal_teardown_language_classifier();
    libpostal_teardown();
    return 0;
}

static struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_near_dupe",
        NULL,
        sizeof(struct module_state),
        near_dupe_methods,
        NULL,
        near_dupe_traverse,
        near_dupe_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit__near_dupe(void) {

#else

#define INITERROR return

void cleanup_libpostal(void) {
    libpostal_teardown();
    libpostal_teardown_language_classifier();
}

void
init_near_dupe(void) {

#endif

#ifdef IS_PY3K
    PyObject *module = PyModule_Create(&module_def);
#else
    PyObject *module = Py_InitModule("_near_dupe", near_dupe_methods);
#endif

    if (module == NULL) {
        INITERROR;
    }
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("_near_dupe.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

   char* datadir = getenv("LIBPOSTAL_DATA_DIR");

    if ((datadir!=NULL) && (!libpostal_setup_datadir(datadir) || !libpostal_setup_language_classifier_datadir(datadir)) ||
        (!libpostal_setup() || !libpostal_setup_language_classifier())) {
            PyErr_SetString(PyExc_TypeError,
                            "Error loading libpostal");
    }

#ifndef IS_PY3K
    Py_AtExit(&cleanup_libpostal);
#endif

#ifdef IS_PY3K
    return module;
#endif
}

