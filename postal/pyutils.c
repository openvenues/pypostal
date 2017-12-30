#include "pyutils.h"


void string_array_destroy(char **strings, size_t num_strings) {
    if (strings != NULL) {
        for (size_t i = 0; i < num_strings; i++) {
            if (strings[i] != NULL) {
                free(strings[i]);
            }
        }
        free(strings);
    }
}


char *PyObject_to_string(PyObject *obj) {
    if (!PyUnicode_Check(obj)) {
        #ifdef IS_PY3K
        if (!PyBytes_Check(obj)) {
            PyErr_SetString(PyExc_TypeError,
                            "Parameter must be bytes or unicode");
        #else
        if (!PyString_Check(obj)) {
            PyErr_SetString(PyExc_TypeError,
                            "Parameter must be string or unicode");
        #endif
            return NULL;
        }
    }       
    PyObject *unistr = PyUnicode_FromObject(obj);        

    if (unistr == NULL) {
        PyErr_SetString(PyExc_TypeError,
                        "Parameter could not be converted to unicode");
        return NULL;
    }

    #ifdef IS_PY3K
        // Python 3 encoding, supported by Python 3.3+

        char *out = PyUnicode_AsUTF8(unistr);

    #else
        // Python 2 encoding

        PyObject *str = PyUnicode_AsEncodedString(unistr, "utf-8", "strict");
        if (str == NULL) {
            PyErr_SetString(PyExc_TypeError,
                            "Parameter could not be utf-8 encoded");
            Py_XDECREF(unistr);
            return 0;
        }

        char *out = PyBytes_AsString(str);

    #endif

    // Need to copy the string, otherwise it's a dup
    char *out_copy = strdup(out);

    #ifndef IS_PY3K
    Py_XDECREF(str);
    #endif
    Py_XDECREF(unistr);

    return out_copy;
}


char **PyObject_to_strings_max_len(PyObject *obj, ssize_t max_len, size_t *num_strings) {
    char **out = NULL;
    size_t n = 0;
    if (!PySequence_Check(obj)) {
        return NULL;
    }

    PyObject *seq = PySequence_Fast(obj, "Expected a sequence");
    Py_ssize_t len = PySequence_Length(obj);

    if (len > 0) {
        out = calloc(len, sizeof(char *));
        if (out == NULL) {
            return NULL;
        }

        char *str = NULL;

        for (int i = 0; i < len; i++) {
            PyObject *item = PySequence_Fast_GET_ITEM(seq, i);

            str = NULL;

            str = PyObject_to_string(item);
            if (str == NULL) {
                PyErr_SetString(PyExc_TypeError, "all elements must be strings");
                goto exit_destroy_strings;
            }

            if (max_len > 0 && strlen(str) >= max_len) {
                PyErr_SetString(PyExc_TypeError, "string exceeded maximum length");
                goto exit_destroy_strings;
            }

            out[i] = str;
            n++;

        }
    }

    if (n > 0) {
        *num_strings = n;
    } else {
        free(out);
        out = NULL;
        *num_strings = 0;
    }

    Py_DECREF(seq);

    return out;

exit_destroy_strings:
    for (size_t i = 0; i < len; i++) {
        char *s = out[i];
        if (s != NULL) {
            free(s);
        }
    }
    free(out);
    Py_DECREF(seq);
    return 0;
}


char **PyObject_to_strings(PyObject *obj, size_t *num_strings) {
    return PyObject_to_strings_max_len(obj, -1, num_strings);
}



PyObject *PyObject_from_strings(char **strings, size_t num_strings) {
    PyObject *result = PyList_New((Py_ssize_t)num_strings);
    if (!result) {
        return NULL;
    }

    for (int i = 0; i < num_strings; i++) {
        char *str = strings[i];
        PyObject *u = PyUnicode_DecodeUTF8((const char *)str, strlen(str), "strict");
        if (u == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        // Note: PyList_SetItem steals a reference, so don't worry about DECREF
        PyList_SetItem(result, (Py_ssize_t)i, u);
    }
    return result;
}


