#include <Python.h>
#include <libpostal/libpostal.h>
#include "pyutils.h"

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

struct module_state {
    PyObject *error;
};


typedef struct language_classifier_response {
    Py_ssize_t num_languages;
    char **languages;
    double *probs;
} language_classifier_response_t;

#ifdef IS_PY3K
    #define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
    #define GETSTATE(m) (&_state)
    static struct module_state _state;
#endif


static PyObject *py_classify_lang_address(PyObject *self, PyObject *args, PyObject *keywords) {
    PyObject *arg_input;

    PyObject *result = NULL;

    if (!PyArg_ParseTuple(args, "O:pylangclassifier", &arg_input)) {
        return 0;
    }

    char *input = PyObject_to_string(arg_input);

    if (input == NULL) {
        return NULL;
    }

    libpostal_language_classifier_response_t *response = libpostal_classify_language(input);

    if (response == NULL) {
        goto exit_free_input;
    }

    result = PyList_New((Py_ssize_t)response->num_languages);
    if (!result) {
        goto exit_destroy_response;
    }

    for (int i = 0; i < response->num_languages; i++) {
        char *language = response->languages[i];
        double prob = response->probs[i];
        PyObject *language_unicode = PyUnicode_DecodeUTF8((const char *)language, strlen(language), "strict");
        if (language_unicode == NULL) {
            Py_DECREF(result);
            goto exit_destroy_response;
        }

        PyObject *tuple = Py_BuildValue("(Od)", language_unicode, prob);
        if (tuple == NULL) {
            Py_DECREF(language_unicode);
            goto exit_destroy_response;
        }

        // Note: PyList_SetItem steals a reference, so don't worry about DECREF
        PyList_SetItem(result, (Py_ssize_t)i, tuple);

        Py_DECREF(language_unicode);
    }

    exit_destroy_response:
        libpostal_language_classifier_response_destroy(response);
    exit_free_input:
        if (input != NULL) {
            free(input);
        }
        return result;
}

static PyMethodDef langclassifier_methods[] = {
    {"classify_lang_address", (PyCFunction)py_classify_lang_address, METH_VARARGS | METH_KEYWORDS,
     "classify_lang_address(text)"},
    {NULL, NULL},
};

#ifdef IS_PY3K

static int langclassifier_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int langclassifier_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    libpostal_teardown();
    libpostal_teardown_language_classifier();
    return 0;
}

static struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_langclassifier",
        NULL,
        sizeof(struct module_state),
        langclassifier_methods,
        NULL,
        langclassifier_traverse,
        langclassifier_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit__langclassifier(void) {
#else

#define INITERROR return

void cleanup_libpostal(void) {
    libpostal_teardown();
    libpostal_teardown_language_classifier();
}

void init_langclassifier(void) {
    #endif

    #ifdef IS_PY3K
        PyObject *module = PyModule_Create(&module_def);
    #else
        PyObject *module = Py_InitModule("_langclassifier", parser_methods);
    #endif

        if (module == NULL) {
            INITERROR;
        }
        struct module_state *st = GETSTATE(module);

        st->error = PyErr_NewException("_langclassifier.Error", NULL, NULL);
        if (st->error == NULL) {
            Py_DECREF(module);
            INITERROR;
        }


        if (!libpostal_setup() || !libpostal_setup_language_classifier()) {
            PyErr_SetString(PyExc_TypeError,
                            "Error loading libpostal data");
        }

    #ifndef IS_PY3K
        Py_AtExit(&cleanup_libpostal);
    #endif


    #ifdef IS_PY3K
        return module;
    #endif
}