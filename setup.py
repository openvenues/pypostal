import os
import subprocess
from subprocess import CalledProcessError

from setuptools import setup, Extension


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
        ext_modules=[
            Extension('postal._expand',
                      sources=['src/postal/pyexpand.c', 'src/postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._parser',
                      sources=['src/postal/pyparser.c', 'src/postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._token_types',
                      sources=['src/postal/pytokentypes.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._tokenize',
                      sources=['src/postal/pytokenize.c', 'src/postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._normalize',
                      sources=['src/postal/pynormalize.c', 'src/postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._near_dupe',
                      sources=['src/postal/pyneardupe.c', 'src/postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._dedupe',
                      sources=['src/postal/pydedupe.c', 'src/postal/pyutils.c'],
                      libraries=['postal'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      extra_compile_args=['-std=c99'],
                      ),
        ],
    )


if __name__ == '__main__':
    main()
