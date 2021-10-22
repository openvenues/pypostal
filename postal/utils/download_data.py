import logging
import os
import os.path
import shutil
import urllib.request
from appdirs import user_data_dir
from pathlib import Path

DATA_DOWNLOAD_URL = 'https://github.com/openvenues/libpostal/releases/download'
APP_DIR = Path(user_data_dir(appname='pypostal', appauthor='openvenues'))

logging.basicConfig()
logger = logging.getLogger('postal.utils.download_data')
logger.setLevel('DEBUG')


def set_data_dir():
    os.environ['LIBPOSTAL_DATA_DIR'] = str(get_data_dir())


def get_data_dir():
    data_dir = APP_DIR / 'datadir'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def clean_data_dir():
    data_dir = get_data_dir()
    backup_dir = APP_DIR / 'datadir.backup'
    temp_backup_dir = APP_DIR / 'datadir.backup-temp'
    shutil.rmtree(temp_backup_dir, ignore_errors=True)
    shutil.move(data_dir, temp_backup_dir)
    shutil.rmtree(backup_dir, ignore_errors=True)
    shutil.move(temp_backup_dir, backup_dir)


def download_data(target_version='v1.0.0'):
    data_dir = get_data_dir()
    data_version_file = data_dir / 'data_version'

    if data_version_file.exists():
        with data_version_file.open(mode='r') as f:
            data_version = f.read().strip()
        if target_version == data_version:
            logger.debug(
                f"Data already downloaded to '{data_dir}' at desired version "
                f"of '{target_version}'."
            )
            return
        else:
            logger.debug(
                f"Existing version '{data_version}' does not match target "
                f"version '{target_version}'. Cleaning up data dir."
            )
            clean_data_dir()

    data_files = [
        'language_classifier.tar.gz',
        'libpostal_data.tar.gz',
        'parser.tar.gz',
    ]

    print(f"Data dir is set to: {data_dir}")

    for data_file in data_files:
        download_url = f'{DATA_DOWNLOAD_URL}/{target_version}/{data_file}'
        target_path = data_dir / data_file
        with urllib.request.urlopen(download_url) as urlf:
            with target_path.open('wb') as localf:
                print(f"Downloading '{data_file}' from '{download_url}'...")
                shutil.copyfileobj(urlf, localf)
        print(f"Unpacking '{data_file}'...")
        shutil.unpack_archive(
            target_path,
            extract_dir=data_dir,
            format='gztar',
        )

    with data_version_file.open('w') as f:
        f.write(target_version)


def ensure_data_available():
    if 'LIBPOSTAL_DATA_DIR' in os.environ:
        logger.debug(
            f"LIBPOSTAL_DATA_DIR is set to '{os.environ['LIBPOSTAL_DATA_DIR']}'. "
            "Skipping download."
        )
    else:
        set_data_dir()
        download_data(target_version='v1.0.0')


if __name__ == '__main__':
    ensure_data_available()
