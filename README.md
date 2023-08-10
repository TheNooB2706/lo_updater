# LibreOffice Updater for Debian
A tool for managing official LibreOffice installation on Debian.

## Why
While LibreOffice can be installed from Debian's own repository, it is not the latest version. Since LibreOffice provides their own `.deb` packages, the latest version can be installed using the packages downloaded from the official site. This tool allows installation to be automated.

# Installation and usage
Precompiled binary can be downloaded at the [release page](https://github.com/TheNooB2706/lo_updater/releases). Alternatively to use the script directly:  
1. Clone the repository
    ```
    git clone https://github.com/TheNooB2706/lo_updater
    ```
    `cd` into the repository directory
    ```
    cd lo_updater
    ```
1. Before installing the dependencies, you might want to create a virtual environment. To do so,
    ```
    python3 -m venv lovenv
    ```
    will create a virtual environment named `lovenv`. Then to activate the environment,
    ```
    source lovenv/bin/activate
    ```
1. Install the dependencies
    ```
    pip3 install -r requirements.txt
    ```
1. To execute the script
    ```
    python3 lo_updater.py
    ```

## Command Line Help
```
usage: lo_updater [-h] [--check-only | --download-only | --remove-only | --install-only ARCHIVE_FILE] [--use-latest-version] [--dry-run] [--dl-dir DL_DIR]

A tool for managing official LibreOffice installation on Debian.

options:
  -h, --help            show this help message and exit
  --check-only, -c      Only check if there is update available.
  --download-only       Skip removal of old version and installation process, only download if there is newer version.
  --remove-only         Remove existing installation of LibreOffice.
  --install-only ARCHIVE_FILE
                        Install downloaded installation archive. Take path to the archive as argument.
  --use-latest-version  Update to the latest version instead of prompting which version to download if there are multiple new versions.
  --dry-run
  --dl-dir DL_DIR, -d DL_DIR
                        Use custom directory for downloading packages.

GitHub project page: https://github.com/TheNooB2706/lo_updater
```

# License
[GNU General Public License version 3](https://opensource.org/licenses/GPL-3.0)