import os
import subprocess

from setuptools import setup, Extension, find_packages

this_dir = os.path.realpath(os.path.dirname(__file__))


VERSION = '1.1.10'


def _check_run(*cmd_parts):
    return subprocess.run(
        cmd_parts,
        stdin=subprocess.DEVNULL,
        check=True,
        capture_output=True,
        encoding='utf-8'
    ).stdout


def _pkgconf_getflags(flag):
    return _check_run('pkgconf', '--print-errors', flag, 'libpostal')


def _pkgconf_parsed(flag):
    res = _pkgconf_getflags(flag)
    return [part[2:] for part in res.strip().split(' ')]


def libpostal_flags_from_env():
    prefix = os.getenv('LIBPOSTAL_PREFIX')
    if prefix is None:
        return None

    return {
        'include_dirs': [os.path.join(prefix, 'include')],
        'library_dirs': [os.path.join(prefix, 'libs')],
    }


def libpostal_flags_from_pkgconf():
    try:
        return {
            'include_dirs': _pkgconf_parsed('--cflags-only-I'),
            'library_dirs': _pkgconf_parsed('--libs-only-L'),
        }
    except FileNotFoundError:
        # If we get this exception, pkgconf was not found
        return None


def libpostal_flags():
    # First, check the env
    config = libpostal_flags_from_env()
    if config is not None:
        return config

    # Then see if pkgconf can find it
    config = libpostal_flags_from_pkgconf()
    if config is not None:
        return config

    # If neither of those worked, just guess the default
    return {
        'include_dirs': ['/usr/local/include'],
        'library_dirs': ['/usr/local/libs'],
    }


_libpostal_flags = libpostal_flags()


def main():
    setup(
        name='postal',
        version=VERSION,
        install_requires=[
            'six',
        ],
        setup_requires=[
            'nose>=1.0'
        ],
        ext_modules=[
            Extension('postal._expand',
                      sources=['postal/pyexpand.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=_libpostal_flags['include_dirs'],
                      library_dirs=_libpostal_flags['library_dirs'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._parser',
                      sources=['postal/pyparser.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=_libpostal_flags['include_dirs'],
                      library_dirs=_libpostal_flags['library_dirs'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._token_types',
                      sources=['postal/pytokentypes.c'],
                      libraries=['postal'],
                      include_dirs=_libpostal_flags['include_dirs'],
                      library_dirs=_libpostal_flags['library_dirs'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._tokenize',
                      sources=['postal/pytokenize.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=_libpostal_flags['include_dirs'],
                      library_dirs=_libpostal_flags['library_dirs'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._normalize',
                      sources=['postal/pynormalize.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=_libpostal_flags['include_dirs'],
                      library_dirs=_libpostal_flags['library_dirs'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._near_dupe',
                      sources=['postal/pyneardupe.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=_libpostal_flags['include_dirs'],
                      library_dirs=_libpostal_flags['library_dirs'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._dedupe',
                      sources=['postal/pydedupe.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=_libpostal_flags['include_dirs'],
                      library_dirs=_libpostal_flags['library_dirs'],
                      extra_compile_args=['-std=c99'],
                      ),
        ],
        packages=find_packages(),
        package_data={
            'postal': ['*.h']
        },
        zip_safe=False,
        url='https://github.com/openvenues/pypostal',
        download_url='https://github.com/openvenues/pypostal/tarball/{}'.format(VERSION),
        description='Python bindings to libpostal for fast international address parsing/normalization',
        license='MIT License',
        maintainer='mapzen.com',
        maintainer_email='pelias@mapzen.com',
        classifiers=[
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: C',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Topic :: Text Processing :: Linguistic',
            'Topic :: Scientific/Engineering :: GIS',
            'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    )


if __name__ == '__main__':
    main()
