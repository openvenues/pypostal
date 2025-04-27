import argparse
import os
import subprocess
import sys
import platform
import shutil
import multiprocessing
import re

from setuptools import setup, Extension, Command, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.install import install
from distutils.errors import DistutilsArgError

this_dir = os.path.realpath(os.path.dirname(__file__))
vendor_dir = os.path.join(this_dir, 'vendor', 'libpostal')

# VERSION = '1.1.10' # Read from pyproject.toml ideally, but setup.py runs first
# For now, let setuptools handle version via pyproject.toml

def get_os_name():
    name = platform.system().lower()
    if name == 'darwin':
        return 'macos'
    return name

def normalize_arch(arch):
    arch = arch.lower()
    if 'arm64' in arch or 'aarch64' in arch:
        return 'arm64'
    elif 'x86_64' in arch or 'amd64' in arch:
        return 'x86_64'
    elif 'x86' in arch or 'i686' in arch or 'win32' in arch:
        return 'x86'
    return arch

def get_libpostal_version():
    version_file = os.path.join(vendor_dir, 'configure.ac')
    if not os.path.exists(version_file):
        return 'unknown'
    with open(version_file) as f:
        content = f.read()
    m = re.search(r'AC_INIT\(\[libpostal], ([0-9]+\.[0-9]+\.[0-9]+)\)', content)
    if m:
        return m.group(1)
    return 'unknown'

def get_libpostal_commit():
    git_dir = os.path.join(vendor_dir, '.git')
    # Try to get the commit hash using git if available
    try:
        result = subprocess.run([
            'git', '--git-dir', git_dir, 'rev-parse', 'HEAD'
        ], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        # Fallback: try to read .git/HEAD directly
        head_file = os.path.join(git_dir, 'HEAD')
        if os.path.exists(head_file):
            with open(head_file) as f:
                ref = f.read().strip()
            if ref.startswith('ref:'):
                ref_path = os.path.join(git_dir, ref.split(' ', 1)[1])
                if os.path.exists(ref_path):
                    with open(ref_path) as rf:
                        return rf.read().strip()
            else:
                return ref
        return 'unknown'

def get_cache_dir():
    os_name = get_os_name()
    arch = normalize_arch(os.environ.get('CIBW_ARCHS', platform.machine()))
    commit = get_libpostal_commit()
    
    # Use a unique subdirectory for each architecture
    # This ensures each arch build goes to a separate directory
    # and prevents sequential builds from overwriting each other
    base_dir = os.path.abspath(os.path.join('build', 'libpostal_install_cache'))
    return os.path.join(base_dir, f'{os_name}-{arch}-libpostal-{commit}')

def get_build_env():
    """Return a dict of environment variables for building libpostal, standardized across OSes."""
    env = os.environ.copy()
    # Always set -fPIC for static linking
    env['CFLAGS'] = env.get('CFLAGS', '') + ' -fPIC'
    # Add platform-specific flags if needed
    if get_os_name() == 'darwin':
        # macOS: nothing extra for now, but could add deployment target, etc.
        pass
    elif get_os_name() == 'linux':
        # Linux: nothing extra for now
        pass
    elif get_os_name() == 'windows':
        # Windows: handled by MSYS2 in CI
        pass
    return env

# Custom build_ext command
class build_ext(_build_ext):
    def clean_libpostal_build_dir(self):
        print("[pypostal] Relaxed cleaning: only running 'make clean' if Makefile exists, and skipping 'git clean -xfd' to avoid deleting build scripts.", flush=True)
        makefile_path = os.path.join(vendor_dir, 'Makefile')
        if os.path.exists(makefile_path):
            try:
                subprocess.check_call(['make', 'clean'], cwd=vendor_dir)
            except Exception as e:
                print(f"[pypostal] Warning: 'make clean' failed: {e}", flush=True)
        else:
            print("[pypostal] Skipping 'make clean': Makefile not found.", flush=True)
        # No longer running 'git clean -xfd' to avoid deleting important build/configure scripts
        # If you want to clean build artifacts, do so more selectively here.

    def run(self):
        cache_base_dir = get_cache_dir()
        norm_arch = normalize_arch(os.environ.get('CIBW_ARCHS', platform.machine()))
        os_name = get_os_name()
        libpostal_commit = get_libpostal_commit()
        libpostal_install_prefix = cache_base_dir
        libpostal_lib_dir = os.path.join(libpostal_install_prefix, 'lib')
        libpostal_include_dir = os.path.join(libpostal_install_prefix, 'include')
        libpostal_static_lib = os.path.join(libpostal_lib_dir, 'libpostal.a')
        print(f"[pypostal] OS: {os_name}, Arch: {norm_arch}, libpostal commit: {libpostal_commit}")
        print(f"[pypostal] Cache dir: {cache_base_dir}")
        print(f"[pypostal] Expected static lib: {libpostal_static_lib}")

        # Check if libpostal is already built for this architecture
        if os.path.exists(libpostal_static_lib):
            print(f"Found cached libpostal build for {norm_arch} at {libpostal_install_prefix}", flush=True)
        else:
            print(f"No cached libpostal build found for {norm_arch}, building now...", flush=True)
            # Clean build dir before every build
            self.clean_libpostal_build_dir()
            # Ensure install directories exist
            os.makedirs(libpostal_install_prefix, exist_ok=True)
            # os.makedirs(libpostal_lib_dir, exist_ok=True) # Created by make install
            # os.makedirs(libpostal_include_dir, exist_ok=True) # Created by make install

            # --- Copy Windows-specific files (if on Windows) --- #
            if platform.system() == 'Windows':
                print("Copying files from vendor/libpostal/windows/ to vendor/libpostal/", flush=True)
                windows_dir = os.path.join(vendor_dir, 'windows')
                if os.path.isdir(windows_dir):
                    # Use shutil.copytree for robustness if Python version allows `dirs_exist_ok`
                    # For simplicity/compatibility, copy file by file
                    for item_name in os.listdir(windows_dir):
                        src_item = os.path.join(windows_dir, item_name)
                        dst_item = os.path.join(vendor_dir, item_name)
                        try:
                            if os.path.isfile(src_item):
                                shutil.copy2(src_item, dst_item)
                            elif os.path.isdir(src_item):
                                # Avoid copying subdirs for now unless needed
                                # shutil.copytree(src_item, dst_item, dirs_exist_ok=True) 
                                pass 
                        except Exception as e:
                            print(f"Warning: Could not copy {src_item} to {dst_item}: {e}", file=sys.stderr)
                else:
                    print("Warning: vendor/libpostal/windows/ directory not found.", file=sys.stderr)
            # --------------------------------------------------- #

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
                # Clean again before make just in case
                self.clean_libpostal_build_dir()
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

        # --- Universal2 static lib build for macOS ---
        if os_name == 'darwin' and 'universal2' in os.environ.get('CIBW_ARCHS', ''):
            x86_prefix = os.path.join(cache_base_dir + '-x86_64')
            arm_prefix = os.path.join(cache_base_dir + '-arm64')
            x86_lib = os.path.join(x86_prefix, 'lib', 'libpostal.a')
            arm_lib = os.path.join(arm_prefix, 'lib', 'libpostal.a')
            # Build for x86_64 if not present
            if not os.path.exists(x86_lib):
                print('::group::Building libpostal for x86_64')
                self.clean_libpostal_build_dir()
                env = get_build_env().copy()
                env['CFLAGS'] = '-arch x86_64 -fPIC'
                env['LDFLAGS'] = '-arch x86_64'
                subprocess.check_call(['./bootstrap.sh'], cwd=vendor_dir, env=env)
                subprocess.check_call([
                    './configure', '--disable-shared', '--enable-static', f'--prefix={x86_prefix}'
                ], cwd=vendor_dir, env=env)
                self.clean_libpostal_build_dir()
                subprocess.check_call(['make', '-j4'], cwd=vendor_dir, env=env)
                subprocess.check_call(['make', 'install'], cwd=vendor_dir, env=env)
                print('::endgroup::')
            # Build for arm64 if not present
            if not os.path.exists(arm_lib):
                print('::group::Building libpostal for arm64')
                self.clean_libpostal_build_dir()
                env = get_build_env().copy()
                env['CFLAGS'] = '-arch arm64 -fPIC'
                env['LDFLAGS'] = '-arch arm64'
                subprocess.check_call(['./bootstrap.sh'], cwd=vendor_dir, env=env)
                subprocess.check_call([
                    './configure', '--disable-shared', '--enable-static', '--disable-sse2', f'--prefix={arm_prefix}'
                ], cwd=vendor_dir, env=env)
                self.clean_libpostal_build_dir()
                subprocess.check_call(['make', '-j4'], cwd=vendor_dir, env=env)
                subprocess.check_call(['make', 'install'], cwd=vendor_dir, env=env)
                print('::endgroup::')
            # Combine with lipo
            print('::group::Creating universal2 libpostal.a with lipo')
            os.makedirs(libpostal_lib_dir, exist_ok=True)
            lipo_cmd = ['lipo', '-create', '-output', libpostal_static_lib, x86_lib, arm_lib]
            print('Running:', ' '.join(lipo_cmd))
            subprocess.check_call(lipo_cmd)
            print('::endgroup::')
            # Diagnostics
            print('::group::Universal2 libpostal.a diagnostics')
            os.system(f'lipo -info "{libpostal_static_lib}"')
            os.system(f'ls -lh "{libpostal_static_lib}"')
            print('::endgroup::')

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

        # Diagnostics after build
        if os.path.exists(libpostal_static_lib):
            print(f"[pypostal] libpostal.a found at: {libpostal_static_lib}")
            if os_name == 'darwin':
                os.system(f'lipo -info "{libpostal_static_lib}"')
            os.system(f'ls -lh "{libpostal_static_lib}"')
        else:
            print(f"[pypostal] ERROR: libpostal.a NOT FOUND at {libpostal_static_lib}", file=sys.stderr)
            sys.exit(1)
        # Print linker flags and .so diagnostics
        print("[pypostal] Extension linker flags and artifact info:")
        for ext in self.extensions:
            print(f"  Extension: {ext.name}")
            print(f"    extra_link_args: {getattr(ext, 'extra_link_args', None)}")
            ext_path = self.get_ext_fullpath(ext.name)
            abs_ext_path = os.path.abspath(ext_path)
            if os.path.exists(abs_ext_path):
                print(f"    .so file: {abs_ext_path}")
                os.system(f'ls -lh "{abs_ext_path}"')
                if os_name == 'darwin':
                    os.system(f'otool -L "{abs_ext_path}"')
            else:
                print(f"    [WARN] .so file not found at {abs_ext_path}")

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
