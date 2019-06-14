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


static PyObject *py_classify_lang_address(PyObject *self, PyObject *args, PyObject *keywords) {
    PyObject *arg_input;

    PyObject *result = NULL;

    static char *kwlist[] = {"address", NULL};


    if (!PyArg_ParseTupleAndKeywords(args, keywords, 
                                     "O|OO:pyparser", kwlist,
                                     &arg_input)) {
        return 0;
    }

    char *input = PyObject_to_string(arg_input);

    if (input == NULL) {
        return NULL;
    }



//    if (!address_dictionary_module_setup(NULL) || !transliteration_module_setup(NULL) || !language_classifier_module_setup(dir)) {
//        log_error("Could not load language classifiers\n");
//        exit(EXIT_FAILURE);
//    }

//    libpostal_address_parser_response_t *parsed = libpostal_parse_address(input, options);
//    if (parsed == NULL) {
//        goto exit_free_country;
//    }
//
//    result = PyList_New((Py_ssize_t)parsed->num_components);
//    if (!result) {
//        goto exit_destroy_response;
//    }
//
//    for (int i = 0; i < parsed->num_components; i++) {
//        char *component = parsed->components[i];
//        char *label = parsed->labels[i];
//        PyObject *component_unicode = PyUnicode_DecodeUTF8((const char *)component, strlen(component), "strict");
//        if (component_unicode == NULL) {
//            Py_DECREF(result);
//            goto exit_destroy_response;
//        }
//
//        PyObject *label_unicode = PyUnicode_DecodeUTF8((const char *)label, strlen(label), "strict");
//        if (label_unicode == NULL) {
//            Py_DECREF(component_unicode);
//            Py_DECREF(result);
//            goto exit_destroy_response;
//        }
//        PyObject *tuple = Py_BuildValue("(OO)", component_unicode, label_unicode);
//        if (tuple == NULL) {
//            Py_DECREF(component_unicode);
//            Py_DECREF(label_unicode);
//            goto exit_destroy_response;
//        }
//
//        // Note: PyList_SetItem steals a reference, so don't worry about DECREF
//        PyList_SetItem(result, (Py_ssize_t)i, tuple);
//
//        Py_DECREF(component_unicode);
//        Py_DECREF(label_unicode);
//    }
//
//    exit_destroy_response:
//        libpostal_address_parser_response_destroy(parsed);
//    exit_free_country:
//        if (country != NULL) {
//            free(country);
//        }
//    exit_free_language:
//        if (language != NULL) {
//            free(language);
//        }
//    exit_free_input:
//        if (input != NULL) {
//            free(input);
//        }
//        return result;
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
//    libpostal_teardown();
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

//void cleanup_libpostal(void) {
//    libpostal_teardown();
//    libpostal_teardown_parser();
//}

void init_parser(void) {
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

