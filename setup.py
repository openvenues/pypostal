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

# ===============================================================================
# Platform & architecture detection utilities
# ===============================================================================

def get_os_name():
    """Return a normalized OS name (macos, linux, windows)."""
    name = platform.system().lower()
    if name == 'darwin':
        return 'macos'
    return name

def normalize_arch(arch):
    """Normalize architecture names to standard values."""
    arch = arch.lower()
    if 'arm64' in arch or 'aarch64' in arch:
        return 'arm64'
    elif 'x86_64' in arch or 'amd64' in arch:
        return 'x86_64'
    elif 'x86' in arch or 'i686' in arch or 'win32' in arch:
        return 'x86'
    return arch

def get_target_arch():
    """Get the target architecture, considering CI environment variables."""
    # CIBW_ARCHS is set by cibuildwheel to the target architecture
    return normalize_arch(os.environ.get('CIBW_ARCHS', platform.machine()))

def is_universal2_build():
    """Check if this is a universal2 build."""
    return 'universal2' in os.environ.get('CIBW_ARCHS', '')

# ===============================================================================
# Version and cache management
# ===============================================================================

def get_libpostal_version():
    """Extract libpostal version from configure.ac."""
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
    """Get the current libpostal commit hash."""
    git_dir = os.path.join(vendor_dir, '.git')
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

def get_cache_dir(arch=None):
    """Get the cache directory for a specific architecture."""
    if arch is None:
        arch = get_target_arch()
    
    os_name = get_os_name()
    commit = get_libpostal_commit()
    
    base_dir = os.path.abspath(os.path.join('build', 'libpostal_install_cache'))
    return os.path.join(base_dir, f'{os_name}-{arch}-libpostal-{commit}')

# ===============================================================================
# Build environment configuration
# ===============================================================================

def get_arch_flags(arch=None):
    """Get architecture-specific compiler and linker flags."""
    if arch is None:
        arch = get_target_arch()
    
    os_name = get_os_name()
    
    cflags = []
    ldflags = []
    
    # Always add -fPIC for shared libraries
    cflags.append("-fPIC")
    
    # Architecture-specific flags
    if os_name == 'macos':
        if arch == 'arm64':
            cflags.append("-arch arm64")
            ldflags.append("-arch arm64")
        elif arch == 'x86_64':
            cflags.append("-arch x86_64")
            ldflags.append("-arch x86_64")
    
    # Special case: SSE2 flags are handled by configure.ac
    # (libpostal automatically disables SSE2 on ARM via --disable-sse2)
    
    return {
        'CFLAGS': ' '.join(cflags),
        'LDFLAGS': ' '.join(ldflags)
    }

def get_configure_options(arch=None, prefix=None):
    """Get configure options for libpostal build."""
    if arch is None:
        arch = get_target_arch()
    
    if prefix is None:
        prefix = get_cache_dir(arch)
    
    options = [
        '--disable-shared',
        '--enable-static',
        f'--prefix={prefix}'
    ]
    
    # Add --disable-sse2 flag for ARM architectures
    if 'arm' in arch:
        options.append('--disable-sse2')
    
    return options

def set_build_env(arch=None):
    """Set the environment variables for building libpostal."""
    arch_flags = get_arch_flags(arch)
    
    # Store original values
    original_cflags = os.environ.get('CFLAGS', '')
    original_ldflags = os.environ.get('LDFLAGS', '')
    
    # Set new values
    os.environ['CFLAGS'] = f"{original_cflags} {arch_flags['CFLAGS']}".strip()
    os.environ['LDFLAGS'] = f"{original_ldflags} {arch_flags['LDFLAGS']}".strip()
    
    print(f"Setting build environment: CFLAGS='{os.environ['CFLAGS']}', LDFLAGS='{os.environ['LDFLAGS']}'", flush=True)
    
    return {
        'CFLAGS': original_cflags,
        'LDFLAGS': original_ldflags
    }

def restore_build_env(original_env):
    """Restore the original environment variables."""
    os.environ['CFLAGS'] = original_env['CFLAGS']
    os.environ['LDFLAGS'] = original_env['LDFLAGS']
    print(f"Restoring environment: CFLAGS='{os.environ['CFLAGS']}', LDFLAGS='{os.environ['LDFLAGS']}'", flush=True)

# ===============================================================================
# Libpostal build functions
# ===============================================================================

def clean_libpostal_build_dir():
    """Clean the libpostal build directory thoroughly."""
    print("[pypostal] Cleaning libpostal build directory thoroughly", flush=True)
    makefile_path = os.path.join(vendor_dir, 'Makefile')
    if os.path.exists(makefile_path):
        try:
            print("[pypostal] Running 'make distclean' for complete cleanup", flush=True)
            subprocess.check_call(['make', 'distclean'], cwd=vendor_dir)
        except Exception as e:
            print(f"[pypostal] Warning: 'make distclean' failed: {e}", flush=True)
            try:
                print("[pypostal] Falling back to 'make clean'", flush=True)
                subprocess.check_call(['make', 'clean'], cwd=vendor_dir)
            except Exception as e2:
                print(f"[pypostal] Warning: 'make clean' also failed: {e2}", flush=True)
    else:
        print("[pypostal] Skipping clean: Makefile not found.", flush=True)
        
    # Remove any stray object files that might not be caught by make clean/distclean
    print("[pypostal] Removing any stray object files", flush=True)
    for root, dirs, files in os.walk(vendor_dir):
        for file in files:
            if file.endswith('.o') or file.endswith('.lo') or file.endswith('.la') or file.endswith('.a'):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"[pypostal] Removed stray object file: {os.path.join(root, file)}", flush=True)
                except Exception as e:
                    print(f"[pypostal] Warning: Could not remove {os.path.join(root, file)}: {e}", flush=True)

def bootstrap_libpostal():
    """Run bootstrap.sh to set up libpostal build."""
    print("[pypostal] Running bootstrap.sh", flush=True)
    try:
        cmd = ['./bootstrap.sh']
        if get_os_name() == 'windows':
            cmd.insert(0, 'sh')
        subprocess.check_call(cmd, cwd=vendor_dir, stdout=sys.stdout, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running bootstrap.sh: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        if isinstance(e, FileNotFoundError):
            print(f"Error: Command '{cmd[0]}' not found. Is MSYS2/sh installed?", file=sys.stderr)
        else:
            print(f"OS error during bootstrap: {e}", file=sys.stderr)
        sys.exit(1)

def configure_libpostal(prefix, arch=None):
    """Configure libpostal with the given prefix and architecture."""
    print(f"[pypostal] Configuring libpostal for {arch if arch else get_target_arch()} with prefix {prefix}", flush=True)
    
    cmd = [
        os.path.join(vendor_dir, 'configure'),
        *get_configure_options(arch=arch, prefix=prefix)
    ]
    
    try:
        subprocess.check_call(cmd, cwd=vendor_dir, stdout=sys.stdout, stderr=sys.stderr)
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

def build_and_install_libpostal():
    """Build and install libpostal to the configured prefix."""
    print("[pypostal] Building and installing libpostal...", flush=True)
    try:
        num_cores = multiprocessing.cpu_count()
        subprocess.check_call(['make', '-j', str(num_cores)], cwd=vendor_dir, 
                             stdout=sys.stdout, stderr=sys.stderr)
        subprocess.check_call(['make', 'install'], cwd=vendor_dir, 
                             stdout=sys.stdout, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running make/make install: {e}", file=sys.stderr)
        sys.exit(1)

def verify_libpostal_arch(lib_path, expected_arch=None):
    """Verify that the built libpostal.a has the expected architecture."""
    if expected_arch is None:
        expected_arch = get_target_arch()
    
    if get_os_name() == 'macos':
        try:
            lipo_output = subprocess.check_output(['lipo', '-info', lib_path], 
                                                stderr=subprocess.STDOUT, text=True)
            print(f"Library architecture: {lipo_output.strip()}", flush=True)
            
            # Check if the expected architecture is present
            if expected_arch not in lipo_output.lower():
                print(f"WARNING: Library does not contain {expected_arch} architecture: {lipo_output}", flush=True)
                return False
            return True
        except Exception as e:
            print(f"Could not check architecture: {e}", flush=True)
    
    # For non-macOS or if lipo check fails, assume it's correct
    return True

def build_libpostal_for_arch(arch):
    """Build libpostal for a specific architecture."""
    print(f"[pypostal] Building libpostal for {arch}", flush=True)
    
    # Get the install prefix for this architecture
    install_prefix = get_cache_dir(arch)
    static_lib_path = os.path.join(install_prefix, 'lib', 'libpostal.a')
    
    # If we're doing a universal2 build, always rebuild each architecture
    # to avoid any potential issues with previous builds
    # force_rebuild = is_universal2_build()
    
    # If library exists with correct architecture and we're not forcing a rebuild, use it
    # Removed force_rebuild check as universal2 is gone
    if os.path.exists(static_lib_path) and verify_libpostal_arch(static_lib_path, arch):
        # NOTE: Caching is currently disabled in workflows, so this path is unlikely to be hit
        print(f"[pypostal] Using cached libpostal build for {arch}", flush=True)
        return static_lib_path
    
    print(f"[pypostal] Need to build libpostal for {arch}", flush=True)
    
    # Clean any previous build using git clean for robustness
    print(f"[pypostal] Running git clean -fdx before {arch} build", flush=True)
    try:
        # Ensure we are in the correct directory relative to setup.py
        if not os.path.exists(os.path.join(vendor_dir, ".git")):
            print(f"[pypostal] Warning: .git directory not found in {vendor_dir}, skipping git clean.", flush=True)
        else:
            subprocess.check_call(['git', 'clean', '-fdx'], cwd=vendor_dir)
    except Exception as e:
        print(f"[pypostal] Warning: git clean failed in {vendor_dir}: {e}", flush=True)
    # clean_libpostal_build_dir() # Replaced with git clean
    
    # Ensure the install directory exists
    os.makedirs(install_prefix, exist_ok=True)
    
    # Store all environment variables that might affect the build
    original_env = {}
    build_env_vars = [
        'CFLAGS', 'CPPFLAGS', 'CXXFLAGS', 'LDFLAGS', 
        'CC', 'CXX', 'LD', 'AR', 'RANLIB', 'ARCHFLAGS'
    ]
    
    for var in build_env_vars:
        original_env[var] = os.environ.get(var, '')
    
    # Explicitly get flags for the target architecture (includes -fPIC)
    arch_flags = get_arch_flags(arch)
    
    # Always set CFLAGS and LDFLAGS for the build
    os.environ['CFLAGS'] = arch_flags['CFLAGS']
    os.environ['LDFLAGS'] = arch_flags['LDFLAGS']
    
    # Handle macOS specific ARCHFLAGS if necessary
    if get_os_name() == 'macos':
        os.environ['ARCHFLAGS'] = arch_flags['CFLAGS'] # macOS uses CFLAGS for ARCHFLAGS sometimes
        print(f"[pypostal] Set architecture flags for {arch}:", flush=True)
        for var in ['CFLAGS', 'CPPFLAGS', 'CXXFLAGS', 'LDFLAGS', 'ARCHFLAGS']:
            print(f"  {var}={os.environ.get(var, '')}", flush=True)
    else:
        # Clear ARCHFLAGS if it exists for non-macOS to avoid confusion
        if 'ARCHFLAGS' in os.environ:
            del os.environ['ARCHFLAGS']
        print(f"[pypostal] Set environment for {arch}: CFLAGS='{os.environ['CFLAGS']}' LDFLAGS='{os.environ['LDFLAGS']}'", flush=True)
    
    try:
        # Bootstrap if needed
        if not os.path.exists(os.path.join(vendor_dir, 'configure')):
            bootstrap_libpostal()
        
        # Configure
        configure_libpostal(install_prefix, arch)
        
        # Build and install
        build_and_install_libpostal()
        
        # Verify build
        if not os.path.exists(static_lib_path):
            print(f"Error: Static library {static_lib_path} not found after build!", file=sys.stderr)
            sys.exit(1)
        
        # Verify architecture with more detailed output
        print(f"[pypostal] Verifying architecture of built library for {arch}", flush=True)
        if get_os_name() == 'macos':
            # Run lipo -info for diagnostic purposes
            lipo_output = subprocess.check_output(['lipo', '-info', static_lib_path], text=True).strip()
            print(f"[pypostal] lipo -info: {lipo_output}", flush=True)
            
            # Run lipo -detailed_info for more detailed architecture information
            try:
                lipo_detailed = subprocess.check_output(['lipo', '-detailed_info', static_lib_path], text=True).strip()
                print(f"[pypostal] Detailed architecture info:\n{lipo_detailed}", flush=True)
            except subprocess.SubprocessError:
                print("[pypostal] Could not get detailed architecture info", flush=True)
            
            # Check if the expected architecture is present
            if arch not in lipo_output.lower():
                print(f"Error: Built library does not have the expected architecture ({arch}): {lipo_output}", file=sys.stderr)
                sys.exit(1)
        
        print(f"[pypostal] Successfully built libpostal for {arch}", flush=True)
        return static_lib_path
    
    finally:
        # Restore original environment
        for var, value in original_env.items():
            if value:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
        print(f"[pypostal] Restored original environment", flush=True)

# ===============================================================================
# Custom build_ext command
# ===============================================================================

class build_ext(_build_ext):
    def run(self):
        # Print diagnostic information
        arch = get_target_arch()
        os_name = get_os_name()
        print(f"[pypostal] Building for OS: {os_name}, Architecture: {arch}", flush=True)
        
        # Store original environment variables
        original_env = {}
        for var in ['CFLAGS', 'LDFLAGS', 'CPPFLAGS', 'CXXFLAGS', 'CC', 'CXX', 'LD', 'ARCHFLAGS',
                   'MACOSX_DEPLOYMENT_TARGET', 'LIBRARY_PATH', 'DYLD_LIBRARY_PATH', 'PKG_CONFIG_PATH']:
            if var in os.environ:
                original_env[var] = os.environ[var]
        
        try:
            # Build libpostal for the current architecture or universal2
            print(f"[pypostal] Building for single architecture: {arch}", flush=True)
            static_lib_path = build_libpostal_for_arch(arch)
            install_prefix = os.path.dirname(os.path.dirname(static_lib_path))
            
            # Get the include and lib directories
            include_dir = os.path.join(install_prefix, 'include')
            lib_dir = os.path.join(install_prefix, 'lib')
            
            # Update Extension paths
            print(f"[pypostal] Updating extension paths: include={include_dir}, lib={lib_dir}", flush=True)
            
            for ext in self.extensions:
                # Clear any existing paths to avoid contamination
                ext.include_dirs = []
                ext.library_dirs = []
                
                # Add our specific paths first
                ext.include_dirs.append(include_dir)
                ext.library_dirs.append(lib_dir)
                
                # Set extra compiler flags to ensure correct architecture in the extension build
                if get_os_name() == 'macos':
                    arch_flags = ['-arch', arch]
                    
                    # Add architecture flags to extension
                    if not hasattr(ext, 'extra_compile_args'):
                        ext.extra_compile_args = []
                    if not hasattr(ext, 'extra_link_args'):
                        ext.extra_link_args = []
                        
                    ext.extra_compile_args.extend(arch_flags)
                    ext.extra_link_args.extend(arch_flags)
                
                print(f"[pypostal] Final paths for {ext.name}:", flush=True)
                print(f"  include_dirs: {ext.include_dirs}", flush=True)
                print(f"  library_dirs: {ext.library_dirs}", flush=True)
                print(f"  extra_compile_args: {ext.extra_compile_args}", flush=True)
                print(f"  extra_link_args: {getattr(ext, 'extra_link_args', [])}", flush=True)
            
            # Set environment variables to help find the library
            os.environ['LIBRARY_PATH'] = lib_dir
            
            # Run the original build_ext command
            print("[pypostal] Running original build_ext command...", flush=True)
            _build_ext.run(self)
            
            # Print diagnostic information about built extensions
            print("[pypostal] Extension build complete. Library details:", flush=True)
            for ext in self.extensions:
                ext_path = self.get_ext_fullpath(ext.name)
                if os.path.exists(ext_path):
                    print(f"  {ext.name}: {ext_path}")
                    if os_name == 'macos':
                        # Use otool to examine the built extension
                        print(f"  Examining {ext_path} with otool:", flush=True)
                        os.system(f'otool -L "{ext_path}"')
                        # Also check architecture of the built extension
                        print(f"  Architecture of {ext_path}:", flush=True)
                        os.system(f'file "{ext_path}"')
                        os.system(f'lipo -info "{ext_path}"')
                else:
                    print(f"  {ext.name}: NOT FOUND")
        
        finally:
            # Restore original environment
            for var, value in original_env.items():
                os.environ[var] = value
            
            # Remove any environment variables that were added
            for var in ['LIBRARY_PATH', 'DYLD_LIBRARY_PATH', 'PKG_CONFIG_PATH']:
                if var not in original_env and var in os.environ:
                    del os.environ[var]
            
            print("[pypostal] Environment restored to original state", flush=True)

# ===============================================================================
# Main setup function
# ===============================================================================

def main():
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
        ext_modules=extensions,
        packages=find_packages(),
        package_data={
            'postal': ['*.h']
        },
        zip_safe=False,
        cmdclass={'build_ext': build_ext},
    )


if __name__ == '__main__':
    main()
