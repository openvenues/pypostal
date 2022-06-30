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


static PyObject *py_parse_address(PyObject *self, PyObject *args, PyObject *keywords) {
    PyObject *arg_input;
    PyObject *arg_language = Py_None;
    PyObject *arg_country = Py_None;

    PyObject *result = NULL;

    static char *kwlist[] = {"address",
                             "language",
                             "country",
                             NULL
                            };


    if (!PyArg_ParseTupleAndKeywords(args, keywords, 
                                     "O|OO:pyparser", kwlist,
                                     &arg_input, &arg_language,
                                     &arg_country
                                     )) {
        return 0;
    }

    char *input = PyObject_to_string(arg_input);

    if (input == NULL) {
        return NULL;
    }

    char *language = NULL;

    if (arg_language != Py_None) {
        language = PyObject_to_string(arg_language);
        if (language == NULL) {
            goto exit_free_input;
        }
    }

    char *country = NULL;

    if (arg_country != Py_None) {
        country = PyObject_to_string(arg_country);
        if (country == NULL) {
            goto exit_free_language;
        }
    }
    
    libpostal_address_parser_options_t options = libpostal_get_address_parser_default_options();
    options.language = language;
    options.country = country;

    libpostal_address_parser_response_t *parsed = libpostal_parse_address(input, options);
    if (parsed == NULL) {
        goto exit_free_country;
    }

    result = PyList_New((Py_ssize_t)parsed->num_components);
    if (!result) {
        goto exit_destroy_response;
    }

    for (int i = 0; i < parsed->num_components; i++) {
        char *component = parsed->components[i];
        char *label = parsed->labels[i];
        PyObject *component_unicode = PyUnicode_DecodeUTF8((const char *)component, strlen(component), "strict");
        if (component_unicode == NULL) {
            Py_DECREF(result);
            goto exit_destroy_response;
        }

        PyObject *label_unicode = PyUnicode_DecodeUTF8((const char *)label, strlen(label), "strict");
        if (label_unicode == NULL) {
            Py_DECREF(component_unicode);
            Py_DECREF(result);
            goto exit_destroy_response;
        }
        PyObject *tuple = Py_BuildValue("(OO)", component_unicode, label_unicode);
        if (tuple == NULL) {
            Py_DECREF(component_unicode);
            Py_DECREF(label_unicode);
            goto exit_destroy_response;
        }

        // Note: PyList_SetItem steals a reference, so don't worry about DECREF
        PyList_SetItem(result, (Py_ssize_t)i, tuple);

        Py_DECREF(component_unicode);
        Py_DECREF(label_unicode);
    }

exit_destroy_response:
    libpostal_address_parser_response_destroy(parsed);
exit_free_country:
    if (country != NULL) {
        free(country);
    }
exit_free_language:
    if (language != NULL) {
        free(language);
    }
exit_free_input:
    if (input != NULL) {
        free(input);
    }
    return result;
}

static PyMethodDef parser_methods[] = {
    {"parse_address", (PyCFunction)py_parse_address, METH_VARARGS | METH_KEYWORDS, "parse_address(text, language, country)"},
    {NULL, NULL},
};



#ifdef IS_PY3K

static int parser_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int parser_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    libpostal_teardown();
    libpostal_teardown_parser();
    return 0;
}

static struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_parser",
        NULL,
        sizeof(struct module_state),
        parser_methods,
        NULL,
        parser_traverse,
        parser_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit__parser(void) {
#else

#define INITERROR return

void cleanup_libpostal(void) {
    libpostal_teardown();
    libpostal_teardown_parser(); 
}

void
init_parser(void) {
#endif

#ifdef IS_PY3K
    PyObject *module = PyModule_Create(&module_def);
#else
    PyObject *module = Py_InitModule("_parser", parser_methods);
#endif

    if (module == NULL) {
        INITERROR;
    }
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("_parser.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

   char* datadir = getenv("LIBPOSTAL_DATA_DIR");

    if ((datadir!=NULL) && (!libpostal_setup_datadir(datadir) || !libpostal_setup_parser_datadir(datadir)) ||
        (!libpostal_setup() || !libpostal_setup_parser())) {
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

