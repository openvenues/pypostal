#include <Python.h>

#include <libpostal/libpostal.h>

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

static PyMethodDef token_types_methods[] = {
    {NULL, NULL},
};

#ifdef IS_PY3K

static int token_types_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int token_types_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_token_types",
        NULL,
        sizeof(struct module_state),
        token_types_methods,
        NULL,
        token_types_traverse,
        token_types_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit__token_types(void) {
#else
#define INITERROR return

void
init_token_types(void) {
#endif

#ifdef IS_PY3K
    PyObject *module = PyModule_Create(&module_def);
#else
    PyObject *module = Py_InitModule("_token_types", token_types_methods);
#endif

    if (module == NULL)
        INITERROR;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("_token_types.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    PyModule_AddObject(module, "TOKEN_TYPE_END", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_END));
    PyModule_AddObject(module, "TOKEN_TYPE_WORD", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_WORD));
    PyModule_AddObject(module, "TOKEN_TYPE_ABBREVIATION", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_ABBREVIATION));
    PyModule_AddObject(module, "TOKEN_TYPE_IDEOGRAPHIC_CHAR", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_IDEOGRAPHIC_CHAR));
    PyModule_AddObject(module, "TOKEN_TYPE_HANGUL_SYLLABLE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_HANGUL_SYLLABLE));
    PyModule_AddObject(module, "TOKEN_TYPE_ACRONYM", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_ACRONYM));
    PyModule_AddObject(module, "TOKEN_TYPE_PHRASE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_PHRASE));
    PyModule_AddObject(module, "TOKEN_TYPE_EMAIL", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_EMAIL));
    PyModule_AddObject(module, "TOKEN_TYPE_URL", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_URL));
    PyModule_AddObject(module, "TOKEN_TYPE_US_PHONE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_US_PHONE));
    PyModule_AddObject(module, "TOKEN_TYPE_INTL_PHONE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_INTL_PHONE));
    PyModule_AddObject(module, "TOKEN_TYPE_NUMERIC", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_NUMERIC));
    PyModule_AddObject(module, "TOKEN_TYPE_ORDINAL", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_ORDINAL));
    PyModule_AddObject(module, "TOKEN_TYPE_ROMAN_NUMERAL", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_ROMAN_NUMERAL));
    PyModule_AddObject(module, "TOKEN_TYPE_IDEOGRAPHIC_NUMBER", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_IDEOGRAPHIC_NUMBER));
    PyModule_AddObject(module, "TOKEN_TYPE_PERIOD", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_PERIOD));
    PyModule_AddObject(module, "TOKEN_TYPE_EXCLAMATION", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_EXCLAMATION));
    PyModule_AddObject(module, "TOKEN_TYPE_QUESTION_MARK", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_QUESTION_MARK));
    PyModule_AddObject(module, "TOKEN_TYPE_COMMA", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_COMMA));
    PyModule_AddObject(module, "TOKEN_TYPE_COLON", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_COLON));
    PyModule_AddObject(module, "TOKEN_TYPE_SEMICOLON", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_SEMICOLON));
    PyModule_AddObject(module, "TOKEN_TYPE_PLUS", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_PLUS));
    PyModule_AddObject(module, "TOKEN_TYPE_AMPERSAND", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_AMPERSAND));
    PyModule_AddObject(module, "TOKEN_TYPE_AT_SIGN", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_AT_SIGN));
    PyModule_AddObject(module, "TOKEN_TYPE_POUND", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_POUND));
    PyModule_AddObject(module, "TOKEN_TYPE_ELLIPSIS", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_ELLIPSIS));
    PyModule_AddObject(module, "TOKEN_TYPE_DASH", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_DASH));
    PyModule_AddObject(module, "TOKEN_TYPE_BREAKING_DASH", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_BREAKING_DASH));
    PyModule_AddObject(module, "TOKEN_TYPE_HYPHEN", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_HYPHEN));
    PyModule_AddObject(module, "TOKEN_TYPE_PUNCT_OPEN", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_PUNCT_OPEN));
    PyModule_AddObject(module, "TOKEN_TYPE_PUNCT_CLOSE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_PUNCT_CLOSE));
    PyModule_AddObject(module, "TOKEN_TYPE_DOUBLE_QUOTE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_DOUBLE_QUOTE));
    PyModule_AddObject(module, "TOKEN_TYPE_SINGLE_QUOTE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_SINGLE_QUOTE));
    PyModule_AddObject(module, "TOKEN_TYPE_OPEN_QUOTE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_OPEN_QUOTE));
    PyModule_AddObject(module, "TOKEN_TYPE_CLOSE_QUOTE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_CLOSE_QUOTE));
    PyModule_AddObject(module, "TOKEN_TYPE_SLASH", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_SLASH));
    PyModule_AddObject(module, "TOKEN_TYPE_BACKSLASH", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_BACKSLASH));
    PyModule_AddObject(module, "TOKEN_TYPE_GREATER_THAN", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_GREATER_THAN));
    PyModule_AddObject(module, "TOKEN_TYPE_LESS_THAN", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_LESS_THAN));
    PyModule_AddObject(module, "TOKEN_TYPE_OTHER", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_OTHER));
    PyModule_AddObject(module, "TOKEN_TYPE_WHITESPACE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_WHITESPACE));
    PyModule_AddObject(module, "TOKEN_TYPE_NEWLINE", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_NEWLINE));
    PyModule_AddObject(module, "TOKEN_TYPE_INVALID_CHAR", PyLong_FromUnsignedLongLong(LIBPOSTAL_TOKEN_TYPE_INVALID_CHAR));

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}