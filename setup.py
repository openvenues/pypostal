import os
import subprocess
from subprocess import CalledProcessError

from setuptools import setup, Extension, find_packages

this_dir = os.path.realpath(os.path.dirname(__file__))


VERSION = '1.1.10'


def pkgconf_output(*options):
    return subprocess.run(
        ['pkgconf', '--print-errors'] + list(options) + ['libpostal'],
        stdin=subprocess.DEVNULL,
        check=True,
        capture_output=True,
        encoding='utf-8',
    ).stdout


include_dirs = ['/usr/local/include']
library_dirs = ['/usr/local/lib']


prefix = os.getenv('LIBPOSTAL_PREFIX')
if prefix is not None:
    include_dirs = [os.path.join(prefix, 'include')]
    library_dirs = [os.path.join(prefix, 'lib')]
else:
    try:
        pkgconf_output('--exists')
        include_dirs = [part[2:] for part in pkgconf_output('--cflags-only-I').strip().split()]
        library_dirs = [part[2:] for part in pkgconf_output('--libs-only-L').strip().split()]
    except (FileNotFoundError, CalledProcessError):
        pass


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
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._parser',
                      sources=['postal/pyparser.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._token_types',
                      sources=['postal/pytokentypes.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._tokenize',
                      sources=['postal/pytokenize.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._normalize',
                      sources=['postal/pynormalize.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._near_dupe',
                      sources=['postal/pyneardupe.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._dedupe',
                      sources=['postal/pydedupe.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
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
