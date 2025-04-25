import argparse
import os
import subprocess
import sys
import platform
import shutil
import multiprocessing

from setuptools import setup, Extension, Command, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.install import install
from distutils.errors import DistutilsArgError

this_dir = os.path.realpath(os.path.dirname(__file__))
vendor_dir = os.path.join(this_dir, 'vendor', 'libpostal')

# VERSION = '1.1.10' # Read from pyproject.toml ideally, but setup.py runs first
# For now, let setuptools handle version via pyproject.toml

# Custom build_ext command
class build_ext(_build_ext):
    def run(self):
        # Define paths
        libpostal_install_prefix = os.path.join(self.build_temp, 'libpostal_install')
        libpostal_lib_dir = os.path.join(libpostal_install_prefix, 'lib')
        libpostal_include_dir = os.path.join(libpostal_install_prefix, 'include')
        libpostal_static_lib = os.path.join(libpostal_lib_dir, 'libpostal.a')

        # Ensure install directories exist
        os.makedirs(libpostal_install_prefix, exist_ok=True)
        os.makedirs(libpostal_lib_dir, exist_ok=True)
        os.makedirs(libpostal_include_dir, exist_ok=True)

        # Check if libpostal source exists and run bootstrap.sh if needed
        configure_path = os.path.join(vendor_dir, 'configure')
        if not os.path.exists(configure_path):
            print("libpostal source not found or configure script missing, running bootstrap.sh", flush=True)
            try:
                # Explicitly use 'sh' for Windows compatibility with MSYS2
                cmd = ['./bootstrap.sh']
                if platform.system() == 'Windows':
                    cmd.insert(0, 'sh')
                subprocess.check_call(cmd, cwd=vendor_dir, stdout=sys.stdout, stderr=sys.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Error running bootstrap.sh: {e}", file=sys.stderr)
                sys.exit(1)
            except OSError as e:
                # Add check for FileNotFoundError which is more specific on Python 3
                if isinstance(e, FileNotFoundError):
                    print(f"Error running bootstrap.sh: Command '{cmd[0]}' not found. Is MSYS2/sh installed and in PATH?", file=sys.stderr)
                else:
                    print(f"Error running bootstrap.sh (OS error): {e}", file=sys.stderr)
                sys.exit(1)

        # --- Determine Target Architecture from cibuildwheel --- 
        # CIBW_ARCHS contains the target architecture (e.g., 'x86_64', 'arm64')
        # Note: It might list multiple if universal2, but configure runs per arch.
        # We rely on the environment set for the specific build invocation.
        target_arch = os.environ.get('CIBW_ARCHS', platform.machine())
        # If CIBW_ARCHS is not set (e.g., local build), fall back to platform.machine()
        print(f"Target architecture detected/set: {target_arch}", flush=True)

        # Configure libpostal
        print(f"Configuring libpostal with prefix {libpostal_install_prefix}", flush=True)
        configure_cmd = [
            os.path.join(vendor_dir, 'configure'), # Use absolute path
            '--disable-shared', 
            '--enable-static', 
            f'--prefix={libpostal_install_prefix}'
        ]

        # Add --disable-sse2 flag ONLY for macOS ARM64 TARGET
        # Check platform.system() for OS and target_arch for the specific build arch
        if platform.system() == 'Darwin' and 'arm64' in target_arch:
            print("Detected macOS ARM64 TARGET, adding --disable-sse2 flag", flush=True)
            configure_cmd.append('--disable-sse2')
        elif platform.system() == 'Darwin':
            print(f"Detected macOS non-ARM64 TARGET ({target_arch}), NOT adding --disable-sse2 flag", flush=True)
        
        # Add other platform-specific flags if needed later

        try:
            # Run configure from within vendor dir for simplicity
            subprocess.check_call(configure_cmd, cwd=vendor_dir, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error running ./configure: {e}", file=sys.stderr)
            # Optional: Capture and print config.log if it exists
            config_log = os.path.join(vendor_dir, 'config.log')
            if os.path.exists(config_log):
                print("--- config.log ---:")
                try:
                    with open(config_log, 'r') as f:
                        print(f.read())
                except Exception as log_e:
                    print(f"(Could not read config.log: {log_e})", file=sys.stderr)
                print("--- End config.log ---:")
            sys.exit(1)

        # Build and install libpostal
        print("Building and installing libpostal...", flush=True)
        try:
            # Clean first (optional)
            subprocess.check_call(['make', 'clean'], cwd=vendor_dir, stdout=sys.stdout, stderr=sys.stderr)
            
            # Build with multiple cores
            num_cores = multiprocessing.cpu_count()
            subprocess.check_call(['make', '-j', str(num_cores)], cwd=vendor_dir, stdout=sys.stdout, stderr=sys.stderr)
            
            # Install to prefix
            subprocess.check_call(['make', 'install'], cwd=vendor_dir, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error running make/make install: {e}", file=sys.stderr)
            sys.exit(1)

        # Check if static library was created
        if not os.path.exists(libpostal_static_lib):
            print(f"Error: Static library {libpostal_static_lib} not found after build!", file=sys.stderr)
            sys.exit(1)

        # Update Extension paths *before* calling the original build_ext
        print(f"Updating extension paths: include={libpostal_include_dir}, lib={libpostal_lib_dir}", flush=True)
        for ext in self.extensions:
            # Add install path to include and library dirs
            ext.include_dirs.insert(0, libpostal_include_dir)
            ext.library_dirs.insert(0, libpostal_lib_dir)
            
            # Remove old absolute paths if they exist (optional, but cleaner)
            ext.include_dirs = [d for d in ext.include_dirs if d not in ('/usr/local/include',)]
            ext.library_dirs = [d for d in ext.library_dirs if d not in ('/usr/local/lib',)]

            # Ensure the src dir isn't duplicated if it was added before
            libpostal_src_dir = os.path.join(vendor_dir, 'src')
            if libpostal_src_dir not in ext.include_dirs:
                 ext.include_dirs.append(libpostal_src_dir)

            print(f"Final paths for {ext.name}: include={ext.include_dirs}, lib={ext.library_dirs}", flush=True)

        # Now, run the original build_ext command
        print("Running original build_ext command...", flush=True)
        _build_ext.run(self)


def main():
    # Most metadata moved to pyproject.toml
    # Define extensions here, paths will be updated by custom build_ext
    extensions = [
            Extension('postal._expand',
                      sources=['postal/pyexpand.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._parser',
                      sources=['postal/pyparser.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._token_types',
                      sources=['postal/pytokentypes.c'],
                      libraries=['postal'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._tokenize',
                      sources=['postal/pytokenize.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._normalize',
                      sources=['postal/pynormalize.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._near_dupe',
                      sources=['postal/pyneardupe.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      extra_compile_args=['-std=c99'],
                      ),
            Extension('postal._dedupe',
                      sources=['postal/pydedupe.c', 'postal/pyutils.c'],
                      libraries=['postal'],
                      extra_compile_args=['-std=c99'],
                      ),
        ]

    setup(
        # Minimal setup() call relies on pyproject.toml for most metadata
        ext_modules=extensions,
        packages=find_packages(),
        package_data={
            'postal': ['*.h'] # Keep C headers needed by extensions
        },
        zip_safe=False, # C extensions generally mean zip_safe=False
        cmdclass={'build_ext': build_ext}, # Use the custom build_ext
    )


if __name__ == '__main__':
    main()
