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


static PyObject *py_place_languages(PyObject *self, PyObject *args) {
    PyObject *arg_labels;
    PyObject *arg_values;

    PyObject *result = Py_None;

    if (!PyArg_ParseTuple(args, "OO:dedupe", &arg_labels, &arg_values)) {
        return 0;
    }

    size_t num_labels = 0;
    char **labels = PyObject_to_strings(arg_labels, &num_labels);

    if (labels == NULL) {
        return NULL;
    }

    size_t num_values = 0;
    char **values = PyObject_to_strings(arg_values, &num_values);

    if (values == NULL) {
        string_array_destroy(labels, num_labels);
        return NULL;
    }

    size_t num_languages = 0;
    char **languages = NULL;

    size_t num_components = num_labels;

    languages = libpostal_place_languages(num_components, labels, values, &num_languages);

    if (languages != NULL) {
        result = PyObject_from_strings(languages, num_languages);
    } else {
        result = Py_None;
        Py_INCREF(Py_None);
    }

    string_array_destroy(values, num_values);
    string_array_destroy(labels, num_labels);

    return result;
}



typedef libpostal_duplicate_status_t (*duplicate_function)(char *, char *, libpostal_duplicate_options_t);


static PyObject *py_is_duplicate(PyObject *self, PyObject *args, PyObject *keywords, duplicate_function dupe_func) {
    PyObject *arg_value1;
    PyObject *arg_value2;
    PyObject *arg_languages = Py_None;
    libpostal_duplicate_options_t options = libpostal_get_default_duplicate_options();

    PyObject *result = Py_None;

    static char *kwlist[] = {"value1",
                             "value2", 
                             "languages",
                             NULL
                            };

    if (!PyArg_ParseTupleAndKeywords(args, keywords,
                                     "OO|O:dedupe", kwlist,
                                     &arg_value1,
                                     &arg_value2,
                                     &arg_languages
                                     )) {
        return 0;
    }

    char *value1 = PyObject_to_string(arg_value1);

    if (value1 == NULL) {
        return 0;
    }

    char *value2 = PyObject_to_string(arg_value2);

    if (value2 == NULL) {
        free(value1);
        return 0;
    }

    size_t num_languages = 0;
    char **languages = NULL;

    if (PySequence_Check(arg_languages)) {
        languages = PyObject_to_strings_max_len(arg_languages, LIBPOSTAL_MAX_LANGUAGE_LEN, &num_languages);
    }

    if (num_languages > 0 && languages != NULL) {
        options.num_languages = num_languages;
        options.languages = languages;
    }

    libpostal_duplicate_status_t status = dupe_func(value1, value2, options);

    result = PyLong_FromSsize_t((ssize_t)status);

    if (languages != NULL) {
        string_array_destroy(languages, num_languages);
    }

    if (value1 != NULL) {
        free(value1);
    }

    if (value2 != NULL) {
        free(value2);
    }

    return result;
}


static PyObject *py_is_name_duplicate(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate(self, args, keywords, libpostal_is_name_duplicate);
}

static PyObject *py_is_street_duplicate(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate(self, args, keywords, libpostal_is_street_duplicate);
}

static PyObject *py_is_house_number_duplicate(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate(self, args, keywords, libpostal_is_house_number_duplicate);
}

static PyObject *py_is_po_box_duplicate(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate(self, args, keywords, libpostal_is_po_box_duplicate);
}

static PyObject *py_is_unit_duplicate(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate(self, args, keywords, libpostal_is_unit_duplicate);
}

static PyObject *py_is_floor_duplicate(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate(self, args, keywords, libpostal_is_floor_duplicate);
}

static PyObject *py_is_postal_code_duplicate(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate(self, args, keywords, libpostal_is_postal_code_duplicate);
}

static PyObject *py_is_toponym_duplicate(PyObject *self, PyObject *args, PyObject *keywords) {
    PyObject *arg_labels1;
    PyObject *arg_values1;
    PyObject *arg_labels2;
    PyObject *arg_values2;

    PyObject *arg_languages = Py_None;
    libpostal_duplicate_options_t options = libpostal_get_default_duplicate_options();
    
    PyObject *result = Py_None;

    static char *kwlist[] = {"labels1",
                             "values1",
                             "labels2",
                             "values2",
                             "languages",
                             NULL
                            };

    if (!PyArg_ParseTupleAndKeywords(args, keywords, 
                                     "OOOO|O:dedupe", kwlist,
                                     &arg_labels1,
                                     &arg_values1,
                                     &arg_labels2,
                                     &arg_values2,
                                     &arg_languages
                                     )) {
        return 0;
    }

    if (!PySequence_Check(arg_labels1) || !PySequence_Check(arg_values1) || !PySequence_Check(arg_labels2) || !PySequence_Check(arg_values2)) {
        PyErr_SetString(PyExc_TypeError,
                        "Input labels and values must be sequences");
        return 0;
    } else if (PySequence_Length(arg_labels1) != PySequence_Length(arg_values1)) {
        PyErr_SetString(PyExc_TypeError,
                        "Input labels1 and values1 arrays must be of equal length");
        return 0;
    } else if (PySequence_Length(arg_labels2) != PySequence_Length(arg_values2)) {
        PyErr_SetString(PyExc_TypeError,
                        "Input labels2 and values2 arrays must be of equal length");
        return 0;
    }

    size_t num_labels1 = 0;
    char **labels1 = PyObject_to_strings(arg_labels1, &num_labels1);

    if (labels1 == NULL) {
        return NULL;
    }

    size_t num_values1 = 0;
    char **values1 = PyObject_to_strings(arg_values1, &num_values1);

    if (values1 == NULL) {
        string_array_destroy(labels1, num_labels1);
        return NULL;
    }

    size_t num_components1 = num_labels1;

    size_t num_labels2 = 0;
    char **labels2 = PyObject_to_strings(arg_labels2, &num_labels2);

    if (labels1 == NULL) {
        return NULL;
    }

    size_t num_values2 = 0;
    char **values2 = PyObject_to_strings(arg_values2, &num_values2);

    if (values2 == NULL) {
        string_array_destroy(labels1, num_labels1);
        string_array_destroy(values1, num_values1);
        string_array_destroy(labels2, num_labels2);
        return NULL;
    }

    size_t num_components2 = num_labels2;

    size_t num_languages = 0;
    char **languages = NULL;

    if (PySequence_Check(arg_languages)) {
        languages = PyObject_to_strings_max_len(arg_languages, LIBPOSTAL_MAX_LANGUAGE_LEN, &num_languages);
    }

    if (num_languages > 0 && languages != NULL) {
        options.num_languages = num_languages;
        options.languages = languages;
    }

    libpostal_duplicate_status_t status = libpostal_is_toponym_duplicate(num_components1, labels1, values1, num_components2, labels2, values2, options);

    result = PyLong_FromSsize_t((ssize_t)status);

    string_array_destroy(labels1, num_labels1);
    string_array_destroy(values1, num_values1);
    string_array_destroy(labels2, num_labels2);
    string_array_destroy(values2, num_values2);

    if (languages != NULL) {
        string_array_destroy(languages, num_languages);
    }

    return result;
}

double *PyObject_to_double_array(PyObject *obj, size_t *num_values) {
    double *out = NULL;
    size_t n = 0;
    if (!PySequence_Check(obj)) {
        return NULL;
    }

    PyObject *seq = PySequence_Fast(obj, "Expected a sequence");
    Py_ssize_t len = PySequence_Length(obj);

    if (len > 0) {
        out = calloc((size_t)len, sizeof(double));
        if (out == NULL) {
            return NULL;
        }

        for (int i = 0; i < len; i++) {
            PyObject *item = PySequence_Fast_GET_ITEM(seq, i);

            double d;

            if (PyFloat_Check(item)) {
                d = PyFloat_AsDouble(item);
            } else if (PyNumber_Check(item)) {
                PyObject *f = PyNumber_Float(item);
                d = PyFloat_AsDouble(f);
                Py_DECREF(f);
            } else {
                PyErr_SetString(PyExc_TypeError,
                                "Scores must be numeric types");
                free(out);
                Py_DECREF(seq);
                return NULL;
            }

            out[i] = d;

            n++;
        }
    }

    *num_values = n;

    Py_DECREF(seq);

    return out;
}

typedef libpostal_fuzzy_duplicate_status_t (*fuzzy_duplicate_function)(size_t, char **, double *, size_t, char **, double *, libpostal_fuzzy_duplicate_options_t);

static PyObject *py_is_duplicate_fuzzy(PyObject *self, PyObject *args, PyObject *keywords, fuzzy_duplicate_function dupe_func) {
    PyObject *arg_tokens1;
    PyObject *arg_scores1;
    PyObject *arg_tokens2;
    PyObject *arg_scores2;

    PyObject *arg_languages = Py_None;
    libpostal_fuzzy_duplicate_options_t options = libpostal_get_default_fuzzy_duplicate_options();

    double needs_review_threshold = options.needs_review_threshold;
    double likely_dupe_threshold = options.likely_dupe_threshold;

    PyObject *result = Py_None;

    static char *kwlist[] = {"tokens1",
                             "scores1",
                             "tokens2",
                             "scores2",
                             "languages",
                             "needs_review_threshold",
                             "likely_dupe_threshold",
                             NULL
                            };

    if (!PyArg_ParseTupleAndKeywords(args, keywords, 
                                     "OOOO|Odd:dedupe", kwlist,
                                     &arg_tokens1,
                                     &arg_scores1,
                                     &arg_tokens2,
                                     &arg_scores2,
                                     &arg_languages,
                                     &needs_review_threshold,
                                     &likely_dupe_threshold
                                     )) {
        return 0;
    }

    if (!PySequence_Check(arg_tokens1) || !PySequence_Check(arg_scores1) || !PySequence_Check(arg_tokens2) || !PySequence_Check(arg_scores2)) {
        PyErr_SetString(PyExc_TypeError,
                        "Input tokens and scores must be sequences");
        return 0;
    } else if (PySequence_Length(arg_tokens1) != PySequence_Length(arg_scores1)) {
        PyErr_SetString(PyExc_TypeError,
                        "Input tokens1 and scores1 arrays must be of equal length");
        return 0;
    } else if (PySequence_Length(arg_tokens2) != PySequence_Length(arg_scores2)) {
        PyErr_SetString(PyExc_TypeError,
                        "Input tokens2 and scores2 arrays must be of equal length");
        return 0;
    }

    size_t num_tokens1 = 0;
    char **tokens1 = PyObject_to_strings(arg_tokens1, &num_tokens1);

    if (tokens1 == NULL) {
        return NULL;
    }

    size_t num_scores1 = 0;
    double *scores1 = PyObject_to_double_array(arg_scores1, &num_scores1);
    if (scores1 == NULL) {
        string_array_destroy(tokens1, num_tokens1);
        return NULL;
    }

    size_t num_components1 = num_tokens1;

    size_t num_tokens2 = 0;
    char **tokens2 = PyObject_to_strings(arg_tokens2, &num_tokens2);

    if (tokens2 == NULL) {
        string_array_destroy(tokens1, num_tokens1);
        free(scores1);
        return NULL;
    }

    size_t num_scores2 = 0;
    double *scores2 = PyObject_to_double_array(arg_scores2, &num_scores2);
    if (scores2 == NULL) {
        string_array_destroy(tokens1, num_tokens1);
        free(scores1);
        string_array_destroy(tokens2, num_tokens2);
        return NULL;
    }

    size_t num_components2 = num_tokens2;

    size_t num_languages = 0;
    char **languages = NULL;

    if (PySequence_Check(arg_languages)) {
        languages = PyObject_to_strings_max_len(arg_languages, LIBPOSTAL_MAX_LANGUAGE_LEN, &num_languages);
    }

    if (num_languages > 0 && languages != NULL) {
        options.num_languages = num_languages;
        options.languages = languages;
    }

    libpostal_fuzzy_duplicate_status_t status = dupe_func(num_components1, tokens1, scores1, num_components2, tokens2, scores2, options);

    result = Py_BuildValue("ld", status.status, status.similarity);

    string_array_destroy(tokens1, num_tokens1);
    free(scores1);
    string_array_destroy(tokens2, num_tokens2);
    free(scores2);

    if (languages != NULL) {
        string_array_destroy(languages, num_languages);
    }

    return result;
}


static PyObject *py_is_name_duplicate_fuzzy(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate_fuzzy(self, args, keywords, libpostal_is_name_duplicate_fuzzy);
}


static PyObject *py_is_street_duplicate_fuzzy(PyObject *self, PyObject *args, PyObject *keywords) {
    return py_is_duplicate_fuzzy(self, args, keywords, libpostal_is_street_duplicate_fuzzy);
}

static PyMethodDef dedupe_methods[] = {
    {"place_languages", (PyCFunction)py_place_languages, METH_VARARGS, "place_languages(labels, values)"},
    {"is_name_duplicate", (PyCFunction)py_is_name_duplicate, METH_VARARGS | METH_KEYWORDS, "is_name_duplicate(value1, value2, languages=None)"},
    {"is_street_duplicate", (PyCFunction)py_is_street_duplicate, METH_VARARGS | METH_KEYWORDS, "is_street_duplicate(value1, value2, **kw)"},
    {"is_house_number_duplicate", (PyCFunction)py_is_house_number_duplicate, METH_VARARGS | METH_KEYWORDS, "is_house_number_duplicate(value1, value2, languages=None)"},
    {"is_po_box_duplicate", (PyCFunction)py_is_po_box_duplicate, METH_VARARGS | METH_KEYWORDS, "is_po_box_duplicate(value1, value2,languages=None)"},
    {"is_unit_duplicate", (PyCFunction)py_is_unit_duplicate, METH_VARARGS | METH_KEYWORDS, "is_unit_duplicate(value1, value2, languages=None)"},
    {"is_floor_duplicate", (PyCFunction)py_is_floor_duplicate, METH_VARARGS | METH_KEYWORDS, "is_floor_duplicate(value1, value2, languages=None)"},
    {"is_postal_code_duplicate", (PyCFunction)py_is_postal_code_duplicate, METH_VARARGS | METH_KEYWORDS, "is_postal_code_duplicate(value1, value2, languages=None)"},
    {"is_toponym_duplicate", (PyCFunction)py_is_toponym_duplicate, METH_VARARGS | METH_KEYWORDS, "is_toponym_duplicate(labels1, values1, labels2, values2, languages=None)"},
    {"is_name_duplicate_fuzzy", (PyCFunction)py_is_name_duplicate_fuzzy, METH_VARARGS | METH_KEYWORDS, "is_name_duplicate_fuzzy(tokens1, scores1, tokens2, scores2, languages=None, **kw)"},
    {"is_street_duplicate_fuzzy", (PyCFunction)py_is_street_duplicate_fuzzy, METH_VARARGS | METH_KEYWORDS, "is_street_duplicate_fuzzy(tokens1, scores1, tokens2, scores2, languages=None, **kw)"},
    {NULL, NULL},
};

#ifdef IS_PY3K

static int dedupe_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int dedupe_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    libpostal_teardown_language_classifier();
    libpostal_teardown();
    return 0;
}

static struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_dedupe",
        NULL,
        sizeof(struct module_state),
        dedupe_methods,
        NULL,
        dedupe_traverse,
        dedupe_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit__dedupe(void) {

#else

#define INITERROR return

void cleanup_libpostal(void) {
    libpostal_teardown();
    libpostal_teardown_language_classifier();
}

void
init_dedupe(void) {

#endif

#ifdef IS_PY3K
    PyObject *module = PyModule_Create(&module_def);
#else
    PyObject *module = Py_InitModule("_dedupe", dedupe_methods);
#endif

    if (module == NULL) {
        INITERROR;
    }
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("_dedupe.Error", NULL, NULL);
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

    PyModule_AddObject(module, "NULL_DUPLICATE_STATUS", PyLong_FromSsize_t(LIBPOSTAL_NULL_DUPLICATE_STATUS));
    PyModule_AddObject(module, "NON_DUPLICATE", PyLong_FromSsize_t(LIBPOSTAL_NON_DUPLICATE));
    PyModule_AddObject(module, "POSSIBLE_DUPLICATE_NEEDS_REVIEW", PyLong_FromSsize_t(LIBPOSTAL_POSSIBLE_DUPLICATE_NEEDS_REVIEW));
    PyModule_AddObject(module, "LIKELY_DUPLICATE", PyLong_FromSsize_t(LIBPOSTAL_LIKELY_DUPLICATE));
    PyModule_AddObject(module, "EXACT_DUPLICATE", PyLong_FromSsize_t(LIBPOSTAL_EXACT_DUPLICATE));

#ifndef IS_PY3K
    Py_AtExit(&cleanup_libpostal);
#endif

#ifdef IS_PY3K
    return module;
#endif
}
