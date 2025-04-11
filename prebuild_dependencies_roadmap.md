# Pypostal Pre-built Dependency Roadmap

**Goal:** Transform `pypostal` into a Python package installable via `pip` (`pip install pypostal`) without requiring users to pre-install the `libpostal` C library or manually manage its data models.

**Core Strategy:**

1.  **Bundle `libpostal`:** Compile `libpostal` from source during the `pypostal` wheel building process and include the compiled library within the wheel.
2.  **Implement Model Management:** Add Python code to `pypostal` to discover, download, store, and configure the `libpostal` language models at runtime.

---

## Phase 1: Project Setup & Modernization

*Objective: Prepare the `pypostal` repository, modernize its packaging, and set up a basic CI workflow.*

*   [x] **1.1: Fork Repository:**
    [x]   Action: Create a fork of the `openvenues/pypostal` repository.
    [x]   Action: Create a dedicated branch for this pre-building effort.
*   [ ] **1.2: Integrate `libpostal` Source:**
    *   Action: Add `openvenues/libpostal` as a git submodule in a `vendor/` directory (`git submodule add https://github.com/openvenues/libpostal.git vendor/libpostal`).
    *   Action: Update `.gitignore` to handle the submodule correctly if needed.
    *   *Outcome:* `libpostal` source code is version-controlled within the `pypostal` repository.
*   [ ] **1.3: Modernize Python Packaging:**
    *   Action: Create `pyproject.toml`.
    *   Action: Define build system requirements (`setuptools`, `wheel`). Check if `cython` is needed.
    *   Action: Specify `build-backend = "setuptools.build_meta"`.
    *   Action: Migrate all metadata (name, version, author, description, license, etc.) from `setup.py`/`setup.cfg` to `[project]` section in `pyproject.toml`.
    *   Action: Define minimal Python version required (`requires-python`).
    *   Action: Define runtime dependencies in `[project.dependencies]` (initially empty or just core requirements, downloader dependencies added later).
    *   Action: Remove `setup.cfg`. Keep `setup.py` for now as it will contain the build logic for the C extension and `libpostal`.
    *   *Outcome:* Project uses `pyproject.toml` for configuration, adhering to modern Python packaging standards.
*   [ ] **1.4: Setup Basic CI/CD (GitHub Actions):**
    *   Action: Remove `.travis.yml` and `appveyor.yml`.
    *   Action: Create `.github/workflows/build_lint.yml` (or similar name).
    *   Action: Configure the workflow to trigger on pushes/pull requests to the main/development branches.
    *   Action: Add steps to:
        *   Check out the code (`actions/checkout@v4` with `submodules: true`).
        *   Set up Python.
        *   (Optional) Run linters/formatters (e.g., `black`, `flake8`).
        *   (Placeholder) Attempt a basic package build (`python -m build --sdist`) - *This will initially fail until Phase 2 is addressed.*
    *   *Outcome:* A basic CI workflow is in place, checking out submodules correctly.

---

## Phase 2: Bundling `libpostal` into Wheels

*Objective: Modify the build process to compile `libpostal` and link it into the `pypostal` C extension, then use `cibuildwheel` to generate multi-platform wheels.*

*   [ ] **2.1: Customize Build Script (`setup.py`):**
    *   Action: Define a custom build step (e.g., subclass `setuptools.command.build_ext.build_ext`).
    *   Action: Implement logic within the custom step to:
        *   Determine the target platform and architecture (needed for conditional flags).
        *   Change directory to `vendor/libpostal`.
        *   Run `./bootstrap.sh` (required for `autotools`).
        *   Run `./configure`:
            *   Use flags to enable static linking if feasible (`--disable-shared --enable-static`). Check `libpostal` configure options.
            *   Set an appropriate temporary install prefix if needed.
            *   **Crucially:** Conditionally add `--disable-sse2` **only** if building for macOS ARM64 (Apple Silicon M1/M2/...). Detect architecture from environment variables (e.g., set by `cibuildwheel`).
        *   Run `make clean` (good practice before build).
        *   Run `make -jN` (use available cores).
        *   Run `make install` (if using an install prefix).
        *   Handle potential build errors.
    *   Action: Configure the `pypostal` C extension (`Extension` object in `setup.py`) to:
        *   Add `vendor/libpostal/src` to `include_dirs`.
        *   Add the directory containing the compiled `libpostal` library (`libpostal.a` or `.so`/`.dylib`) to `library_dirs`.
        *   Add `postal` to `libraries`.
    *   *Outcome:* Running `python setup.py build_ext` locally (with build dependencies installed) successfully compiles `libpostal` and the `pypostal` extension.
*   [ ] **2.2: Integrate `cibuildwheel` into CI:**
    *   Action: Update/Create the GitHub Actions workflow (`.github/workflows/build_wheels.yml`).
    *   Action: Use the `cibuildwheel` action or run it directly.
    *   Action: Configure the target platforms (`CIBW_PLATFORM` or matrix): Linux (`manylinux_*`), macOS (x86_64, arm64), Windows (amd64).
    *   Action: Use `CIBW_BEFORE_BUILD` to install `libpostal`'s build dependencies for each OS:
        *   Linux: `apt-get update && apt-get install -y autoconf automake libtool pkg-config curl build-essential`
        *   macOS: `brew install autoconf automake libtool pkg-config curl`
        *   Windows: Use `choco` or direct downloads for MSys2/MinGW tools if necessary, or rely on standard GitHub Actions Windows runners having necessary tools. Install `autoconf automake libtool pkg-config curl gcc` via `pacman` within MSys2 environment.
    *   Action: Set `CIBW_ENVIRONMENT` to pass necessary variables if needed (e.g., maybe related to static linking).
    *   Action: Define `CIBW_TEST_COMMAND`:
        *   Install the built wheel (`pip install {package}`).
        *   Run a basic Python import test: `python -c "import postal; print('pypostal imported successfully')"`. *Note: Full initialization will fail until Phase 3.*
    *   Action: Configure the workflow to upload the generated wheels (`dist/*.whl`) as build artifacts.
    *   *Outcome:* CI successfully builds binary wheels for all target platforms and architectures.

---

## Phase 3: Runtime Model Management

*Objective: Implement Python code within `pypostal` to handle the discovery, download, caching, and loading of `libpostal` data models.*

*   [ ] **3.1: Design Model Hosting & Manifest:**
    *   Action: Decide on hosting location for `libpostal` data tarballs (e.g., GitHub Releases, S3). Confirm stability of existing URLs or plan for re-hosting.
    *   Action: Define the structure of `models.json` manifest file (versions, URLs, sha256 checksums, file sizes).
    *   Action: Create the initial `models.json` for the default model.
    *   Action: Host the `models.json` file (e.g., alongside models or potentially bundled in the wheel).
    *   *Outcome:* Clear plan for where models and metadata live.
*   [ ] **3.2: Implement Downloader Module (`postal/downloader.py`):**
    *   Action: Create the `postal/downloader.py` file.
    *   Action: Add runtime dependencies (`requests`, `platformdirs`, `tqdm`) to `pyproject.toml` under `[project.dependencies]`.
    *   Action: Implement `get_cache_dir()` using `platformdirs`.
    *   Action: Implement `list_available_models()` (fetches/parses `models.json`).
    *   Action: Implement `get_downloaded_models()` (scans cache directory).
    *   Action: Implement `download_model(version='latest', force=False)`:
        *   Fetch manifest if needed.
        *   Resolve version ('latest').
        *   Check cache.
        *   Download (use `requests`, `tqdm`, streaming).
        *   Verify checksum.
        *   Extract tarball (`tarfile`) to versioned subdirectory in cache (e.g., `~/.cache/pypostal/models/libpostal_data-vX.X/data`).
        *   Implement robust error handling.
    *   Action: Implement `get_data_dir(version='latest')` returning the path to the extracted *data* directory.
    *   *Outcome:* Python module capable of managing model downloads and cache.
*   [ ] **3.3: Integrate Model Loading into `pypostal`:**
    *   Action: Identify the C API call in `libpostal` used to set the data directory at runtime (likely `libpostal_setup_datadir()` based on README examples).
    *   Action: **Verify/Modify `pypostal` C Extension:** Ensure a Python-callable function exists in `pypostal`'s C code that accepts a path string and calls the appropriate `libpostal` setup function (e.g., `libpostal_setup_datadir()`). Add or modify if necessary. Rebuild extension.
    *   Action: Modify `postal/__init__.py` or a core setup function (e.g., `postal.init()`):
        *   Allow specifying a desired model version (optional, default to 'latest' or a pinned version).
        *   On initialization, call `downloader.get_data_dir()` to find the required model data path.
        *   If path is `None`: Raise an informative `FileNotFoundError` or `PostalDataNotFound` exception guiding the user to run `postal.download_model()`.
        *   If path exists: Call the C extension function to pass this path to `libpostal`'s setup routine *before* any parsing/expansion functions are used.
    *   Action: Expose the `download_model` function publicly (e.g., `from postal import download_model`).
    *   *Outcome:* `pypostal` automatically uses downloaded data on initialization, or provides clear instructions if data is missing.
*   [ ] **3.4: Update CI Test Command:**
    *   Action: Modify `CIBW_TEST_COMMAND` in the wheel building workflow.
    *   Action: Add steps to:
        *   Run `python -c "from postal import download_model; download_model()"`. (May need adjustments for testing environments without network access - potentially pre-downloading in an earlier step or mocking).
        *   Run `python -c "from postal import init, expand, parse; init(); print(expand.expand_address('test')); print(parse.parse_address('test'))"`.
    *   *Outcome:* CI tests validate the download mechanism and basic end-to-end functionality using the bundled library and downloaded data.

---

## Phase 4: Documentation & Testing

*Objective: Update documentation for the new installation and usage patterns, and add comprehensive tests.*

*   [ ] **4.1: Update `README.md`:**
    *   Action: Replace installation instructions with `pip install pypostal`.
    *   Action: Remove prerequisites about compiling `libpostal`.
    *   Action: Add section explaining automatic model downloading and caching.
    *   Action: Document `postal.download_model()` usage.
    *   Action: Document how to specify different model versions if implemented.
    *   Action: Update examples if initialization changed.
    *   *Outcome:* README accurately reflects the new user experience.
*   [ ] **4.2: Add Unit & Integration Tests:**
    *   Action: Add unit tests for `postal.downloader` (mocking network, filesystem).
    *   Action: Add integration tests (using `pytest`?) that:
        *   Perform actual downloads (can be marked or skipped in environments without network).
        *   Verify initialization works with downloaded data.
        *   Test `expand_address` and `parse_address` with known inputs/outputs.
        *   Test error handling when data is missing.
    *   Action: Integrate test execution into the CI workflow (run after wheel installation).
    *   *Outcome:* Robust test suite validating core functionality.

---

## Phase 5: Release

*Objective: Prepare and publish the new version of `pypostal`.*

*   [ ] **5.1: Version Bump:** Decide on new version number (significant change, likely `2.0.0` or similar). Update `pyproject.toml`.
*   [ ] **5.2: Final Testing:** Perform thorough testing across all supported platforms.
*   [ ] **5.3: Tag Release:** Create git tag for the release.
*   [ ] **5.4: Publish to PyPI:** Configure CI to automatically build wheels on tag and upload to PyPI using an API token.
*   [ ] **5.5: Update `pypostal` Main Repository:** Merge changes from fork/branch back into the main `openvenues/pypostal` repository (requires coordination).

---

## Future Considerations / Enhancements

*   Support for alternative models (e.g., `MODEL=senzing`).
*   Configuration options for cache directory location.
*   Allowing users to provide pre-downloaded/extracted model data directories.
*   Investigate static linking vs shared library bundling trade-offs more deeply.
