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
        # --- Determine Target Architecture from cibuildwheel --- 
        target_arch = os.environ.get('CIBW_ARCHS', platform.machine())
        # Normalize arch string for directory naming (e.g., x86_64 -> x86_64)
        # This handles potential variations like 'native' or lists in CIBW_ARCHS
        # A simple approach for now, might need refinement for universal2 etc.
        if 'arm64' in target_arch or 'aarch64' in target_arch:
            norm_arch = 'arm64' # Use a consistent name
        elif 'x86_64' in target_arch or 'AMD64' in target_arch:
             norm_arch = 'x86_64'
        elif 'x86' in target_arch or 'i686' in target_arch or 'win32' in target_arch:
             norm_arch = 'x86'
        else:
             norm_arch = target_arch # Use as-is if unknown
        print(f"Normalized target architecture for cache dir: {norm_arch}", flush=True)

        # Define shared, architecture-specific paths
        # Use a directory outside the standard temp build dir to persist across python versions
        cache_base_dir = os.path.abspath(os.path.join('build', 'libpostal_install_cache'))
        libpostal_install_prefix = os.path.join(cache_base_dir, norm_arch)
        libpostal_lib_dir = os.path.join(libpostal_install_prefix, 'lib')
        libpostal_include_dir = os.path.join(libpostal_install_prefix, 'include')
        libpostal_static_lib = os.path.join(libpostal_lib_dir, 'libpostal.a')

        # Check if libpostal is already built for this architecture
        if os.path.exists(libpostal_static_lib):
            print(f"Found cached libpostal build for {norm_arch} at {libpostal_install_prefix}", flush=True)
        else:
            print(f"No cached libpostal build found for {norm_arch}, building now...", flush=True)
            # Ensure install directories exist
            os.makedirs(libpostal_install_prefix, exist_ok=True)
            # os.makedirs(libpostal_lib_dir, exist_ok=True) # Created by make install
            # os.makedirs(libpostal_include_dir, exist_ok=True) # Created by make install

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

            # Configure libpostal
            print(f"Configuring libpostal with prefix {libpostal_install_prefix}", flush=True)
            configure_cmd = [
                os.path.join(vendor_dir, 'configure'), # Use absolute path
                '--disable-shared', 
                '--enable-static', 
                f'--prefix={libpostal_install_prefix}'
            ]

            # Add --disable-sse2 flag ONLY for ARM64 targets (macOS or Linux)
            if 'arm64' in norm_arch:
                # Check if already added for macOS to avoid duplicates, though harmless
                if '--disable-sse2' not in configure_cmd:
                     print(f"Detected ARM64 TARGET ({platform.system()}), adding --disable-sse2 flag", flush=True)
                     configure_cmd.append('--disable-sse2')
            elif platform.system() == 'Darwin': # Explicitly log for non-arm macOS
                 print(f"Detected macOS non-ARM64 TARGET ({norm_arch}), NOT adding --disable-sse2 flag", flush=True)
            
            # Add other platform-specific flags if needed later

            # --- Set CFLAGS for PIC --- #
            original_cflags = os.environ.get('CFLAGS', '')
            pic_cflags = original_cflags + ' -fPIC'
            print(f"Temporarily setting CFLAGS to: {pic_cflags}", flush=True)
            os.environ['CFLAGS'] = pic_cflags

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
                # --- Restore CFLAGS --- #
                print(f"Restoring CFLAGS to: {original_cflags}", flush=True)
                os.environ['CFLAGS'] = original_cflags
                sys.exit(1)
            # except Exception as e: # Catch other potential errors
            #     # --- Restore CFLAGS --- #
            #     print(f"Restoring CFLAGS due to other error: {original_cflags}", flush=True)
            #     os.environ['CFLAGS'] = original_cflags
            #     raise e

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
                # --- Restore CFLAGS --- #
                print(f"Restoring CFLAGS after make error: {original_cflags}", flush=True)
                os.environ['CFLAGS'] = original_cflags
                sys.exit(1)
            # except Exception as e:
            #     # --- Restore CFLAGS --- #
            #     print(f"Restoring CFLAGS after other make error: {original_cflags}", flush=True)
            #     os.environ['CFLAGS'] = original_cflags
            #     raise e
            finally:
                 # --- Restore CFLAGS --- #
                 # Ensure CFLAGS is restored even if make succeeds
                 print(f"Restoring CFLAGS after libpostal build: {original_cflags}", flush=True)
                 os.environ['CFLAGS'] = original_cflags

            # Check if static library was created
            if not os.path.exists(libpostal_static_lib):
                print(f"Error: Static library {libpostal_static_lib} not found after build!", file=sys.stderr)
                sys.exit(1)
            else:
                 print(f"Successfully built and installed libpostal for {norm_arch} to {libpostal_install_prefix}", flush=True)

        # ----- End of Conditional Build ----- #

        # Update Extension paths *before* calling the original build_ext
        # Always point to the shared architecture-specific cache location
        print(f"Updating extension paths to use cache: include={libpostal_include_dir}, lib={libpostal_lib_dir}", flush=True)
        for ext in self.extensions:
            # Add install path to include and library dirs
            ext.include_dirs.insert(0, libpostal_include_dir)
            ext.library_dirs.insert(0, libpostal_lib_dir)
            
            # Remove old absolute/relative paths if they exist (optional, but cleaner)
            ext.include_dirs = [d for d in ext.include_dirs if d not in ('/usr/local/include',)]
            ext.library_dirs = [d for d in ext.library_dirs if d not in ('/usr/local/lib',)]

            # Ensure the src dir isn't duplicated if it was added before
            # libpostal_src_dir = os.path.join(vendor_dir, 'src')
            # if libpostal_src_dir not in ext.include_dirs:
            #      ext.include_dirs.append(libpostal_src_dir)
            # Keep src dir include? Headers from install prefix should be sufficient.
            ext.include_dirs = [d for d in ext.include_dirs if 'vendor/libpostal/src' not in d]


            print(f"Final paths for {ext.name}: include={ext.include_dirs}, lib={ext.library_dirs}", flush=True)

        # --- Set environment variables to help find the library --- #
        # On macOS, LIBRARY_PATH can help the linker find libraries
        print(f"Setting LIBRARY_PATH to: {libpostal_lib_dir}", flush=True)
        os.environ['LIBRARY_PATH'] = libpostal_lib_dir
        # On Linux/others, LD_LIBRARY_PATH is used at runtime, but LIBRARY_PATH might sometimes be used at link time too.
        # os.environ['LD_LIBRARY_PATH'] = libpostal_lib_dir # Might be needed later if runtime loading fails

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
