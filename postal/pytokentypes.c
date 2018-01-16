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

    PyModule_AddIntConstant(module, "TOKEN_TYPE_END", LIBPOSTAL_TOKEN_TYPE_END);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_WORD", LIBPOSTAL_TOKEN_TYPE_WORD);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_ABBREVIATION", LIBPOSTAL_TOKEN_TYPE_ABBREVIATION);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_IDEOGRAPHIC_CHAR", LIBPOSTAL_TOKEN_TYPE_IDEOGRAPHIC_CHAR);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_HANGUL_SYLLABLE", LIBPOSTAL_TOKEN_TYPE_HANGUL_SYLLABLE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_ACRONYM", LIBPOSTAL_TOKEN_TYPE_ACRONYM);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_PHRASE", LIBPOSTAL_TOKEN_TYPE_PHRASE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_EMAIL", LIBPOSTAL_TOKEN_TYPE_EMAIL);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_URL", LIBPOSTAL_TOKEN_TYPE_URL);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_US_PHONE", LIBPOSTAL_TOKEN_TYPE_US_PHONE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_INTL_PHONE", LIBPOSTAL_TOKEN_TYPE_INTL_PHONE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_NUMERIC", LIBPOSTAL_TOKEN_TYPE_NUMERIC);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_ORDINAL", LIBPOSTAL_TOKEN_TYPE_ORDINAL);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_ROMAN_NUMERAL", LIBPOSTAL_TOKEN_TYPE_ROMAN_NUMERAL);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_IDEOGRAPHIC_NUMBER", LIBPOSTAL_TOKEN_TYPE_IDEOGRAPHIC_NUMBER);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_PERIOD", LIBPOSTAL_TOKEN_TYPE_PERIOD);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_EXCLAMATION", LIBPOSTAL_TOKEN_TYPE_EXCLAMATION);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_QUESTION_MARK", LIBPOSTAL_TOKEN_TYPE_QUESTION_MARK);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_COMMA", LIBPOSTAL_TOKEN_TYPE_COMMA);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_COLON", LIBPOSTAL_TOKEN_TYPE_COLON);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_SEMICOLON", LIBPOSTAL_TOKEN_TYPE_SEMICOLON);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_PLUS", LIBPOSTAL_TOKEN_TYPE_PLUS);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_AMPERSAND", LIBPOSTAL_TOKEN_TYPE_AMPERSAND);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_AT_SIGN", LIBPOSTAL_TOKEN_TYPE_AT_SIGN);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_POUND", LIBPOSTAL_TOKEN_TYPE_POUND);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_ELLIPSIS", LIBPOSTAL_TOKEN_TYPE_ELLIPSIS);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_DASH", LIBPOSTAL_TOKEN_TYPE_DASH);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_BREAKING_DASH", LIBPOSTAL_TOKEN_TYPE_BREAKING_DASH);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_HYPHEN", LIBPOSTAL_TOKEN_TYPE_HYPHEN);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_PUNCT_OPEN", LIBPOSTAL_TOKEN_TYPE_PUNCT_OPEN);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_PUNCT_CLOSE", LIBPOSTAL_TOKEN_TYPE_PUNCT_CLOSE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_DOUBLE_QUOTE", LIBPOSTAL_TOKEN_TYPE_DOUBLE_QUOTE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_SINGLE_QUOTE", LIBPOSTAL_TOKEN_TYPE_SINGLE_QUOTE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_OPEN_QUOTE", LIBPOSTAL_TOKEN_TYPE_OPEN_QUOTE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_CLOSE_QUOTE", LIBPOSTAL_TOKEN_TYPE_CLOSE_QUOTE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_SLASH", LIBPOSTAL_TOKEN_TYPE_SLASH);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_BACKSLASH", LIBPOSTAL_TOKEN_TYPE_BACKSLASH);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_GREATER_THAN", LIBPOSTAL_TOKEN_TYPE_GREATER_THAN);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_LESS_THAN", LIBPOSTAL_TOKEN_TYPE_LESS_THAN);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_OTHER", LIBPOSTAL_TOKEN_TYPE_OTHER);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_WHITESPACE", LIBPOSTAL_TOKEN_TYPE_WHITESPACE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_NEWLINE", LIBPOSTAL_TOKEN_TYPE_NEWLINE);
    PyModule_AddIntConstant(module, "TOKEN_TYPE_INVALID_CHAR", LIBPOSTAL_TOKEN_TYPE_INVALID_CHAR);

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}