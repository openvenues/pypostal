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

static PyObject *py_normalize_string(PyObject *self, PyObject *args) 
{
    PyObject *arg1;
    uint64_t options;
    if (!PyArg_ParseTuple(args, "OK:normalize", &arg1, &options)) {
        return 0;
    }

    char *input = PyObject_to_string(arg1);

    if (input == NULL) {
        return 0;
    }

    char *normalized = libpostal_normalize_string(input, options);

    free(input);
    if (normalized == NULL) {
        return 0;
    }

    PyObject *result = PyUnicode_DecodeUTF8((const char *)normalized, strlen(normalized), "strict");
    free(normalized);
    if (result == NULL) {
            PyErr_SetString(PyExc_ValueError,
                            "Result could not be utf-8 decoded");
            return 0;
    }

    return result;
}


static PyObject *py_normalized_tokens(PyObject *self, PyObject *args) 
{
    PyObject *arg1;
    uint64_t string_options = LIBPOSTAL_NORMALIZE_DEFAULT_STRING_OPTIONS;
    uint64_t token_options = LIBPOSTAL_NORMALIZE_DEFAULT_TOKEN_OPTIONS;
    uint32_t arg_whitespace = 0;

    PyObject *result = NULL;

    if (!PyArg_ParseTuple(args, "O|KKI:normalize", &arg1, &string_options, &token_options, &arg_whitespace)) {
        return 0;
    }

    char *input = PyObject_to_string(arg1);

    if (input == NULL) {
        return 0;
    }

    bool whitespace = arg_whitespace;

    size_t num_tokens;
    libpostal_normalized_token_t *normalized_tokens = libpostal_normalized_tokens(input, string_options, token_options, whitespace, &num_tokens);
    free(input);

    if (normalized_tokens == NULL) {
        return 0;
    }

    result = PyList_New((Py_ssize_t)num_tokens);
    if (!result) {
        goto exit_free_normalized_tokens;
    }

    for (size_t i = 0; i < num_tokens; i++) {
        libpostal_normalized_token_t normalized_token = normalized_tokens[i];
        char *token_str = normalized_token.str;
        PyObject *py_token = PyUnicode_DecodeUTF8((const char *)token_str, strlen(token_str), "strict");
        if (py_token == NULL) {
            Py_DECREF(result);
            goto exit_free_normalized_tokens;
        }

        PyObject *t = PyTuple_New(2);
        PyObject *py_token_type = PyLong_FromLong(normalized_token.token.type);

        PyTuple_SetItem(t, 0, py_token);
        PyTuple_SetItem(t, 1, py_token_type);

        // Note: PyList_SetItem steals a reference, so don't worry about DECREF
        PyList_SetItem(result, (Py_ssize_t)i, t);
    }

    for (size_t i = 0; i < num_tokens; i++) {
        free(normalized_tokens[i].str);
    }
    free(normalized_tokens);


    return result;
exit_free_normalized_tokens:
    for (size_t i = 0; i < num_tokens; i++) {
        free(normalized_tokens[i].str);
    }
    free(normalized_tokens);
    return 0;
}


static PyMethodDef normalize_methods[] = {
    {"normalize_string", (PyCFunction)py_normalize_string, METH_VARARGS, "normalize_string(input, options)"},
    {"normalized_tokens", (PyCFunction)py_normalized_tokens, METH_VARARGS, "normalize_token(input, string_options, token_options, whitespace)"},
    {NULL, NULL},
};



#ifdef IS_PY3K

static int normalize_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int normalize_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_normalize",
        NULL,
        sizeof(struct module_state),
        normalize_methods,
        NULL,
        normalize_traverse,
        normalize_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit_normalize(void) {
#else
#define INITERROR return

void
init_normalize(void) {
#endif

#ifdef IS_PY3K
    PyObject *module = PyModule_Create(&module_def);
#else
    PyObject *module = Py_InitModule("_normalize", normalize_methods);
#endif

    if (module == NULL)
        INITERROR;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("_normalize.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    if (!libpostal_setup()) {
        PyErr_SetString(PyExc_RuntimeError,
                        "Could not load libpostal");
        Py_DECREF(module);
        INITERROR;
    }

    PyModule_AddObject(module, "NORMALIZE_STRING_LATIN_ASCII", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_LATIN_ASCII));
    PyModule_AddObject(module, "NORMALIZE_STRING_TRANSLITERATE", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_TRANSLITERATE));
    PyModule_AddObject(module, "NORMALIZE_STRING_STRIP_ACCENTS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_STRIP_ACCENTS));
    PyModule_AddObject(module, "NORMALIZE_STRING_DECOMPOSE", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_DECOMPOSE));
    PyModule_AddObject(module, "NORMALIZE_STRING_COMPOSE", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_COMPOSE));
    PyModule_AddObject(module, "NORMALIZE_STRING_LOWERCASE", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_LOWERCASE));
    PyModule_AddObject(module, "NORMALIZE_STRING_TRIM", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_TRIM));
    PyModule_AddObject(module, "NORMALIZE_STRING_REPLACE_HYPHENS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_REPLACE_HYPHENS));
    PyModule_AddObject(module, "NORMALIZE_STRING_SIMPLE_LATIN_ASCII", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_STRING_SIMPLE_LATIN_ASCII));


    PyModule_AddObject(module, "NORMALIZE_TOKEN_REPLACE_HYPHENS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_REPLACE_HYPHENS));
    PyModule_AddObject(module, "NORMALIZE_TOKEN_DELETE_HYPHENS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_DELETE_HYPHENS));
    PyModule_AddObject(module, "NORMALIZE_TOKEN_DELETE_FINAL_PERIOD", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_DELETE_FINAL_PERIOD));
    PyModule_AddObject(module, "NORMALIZE_TOKEN_DELETE_ACRONYM_PERIODS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_DELETE_ACRONYM_PERIODS));
    PyModule_AddObject(module, "NORMALIZE_TOKEN_DROP_ENGLISH_POSSESSIVES", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_DROP_ENGLISH_POSSESSIVES));
    PyModule_AddObject(module, "NORMALIZE_TOKEN_DELETE_OTHER_APOSTROPHE", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_DELETE_OTHER_APOSTROPHE));
    PyModule_AddObject(module, "NORMALIZE_TOKEN_SPLIT_ALPHA_FROM_NUMERIC", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_SPLIT_ALPHA_FROM_NUMERIC));
    PyModule_AddObject(module, "NORMALIZE_TOKEN_REPLACE_DIGITS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_REPLACE_DIGITS));


    PyModule_AddObject(module, "NORMALIZE_DEFAULT_STRING_OPTIONS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_DEFAULT_STRING_OPTIONS));
    PyModule_AddObject(module, "NORMALIZE_DEFAULT_TOKEN_OPTIONS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_DEFAULT_TOKEN_OPTIONS));

    PyModule_AddObject(module, "NORMALIZE_TOKEN_OPTIONS_DROP_PERIODS", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_TOKEN_OPTIONS_DROP_PERIODS));

    PyModule_AddObject(module, "NORMALIZE_DEFAULT_TOKEN_OPTIONS_NUMERIC", PyLong_FromUnsignedLongLong(LIBPOSTAL_NORMALIZE_DEFAULT_TOKEN_OPTIONS_NUMERIC));


#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
