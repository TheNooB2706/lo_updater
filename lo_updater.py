import updater
import argparse
import sys
import pathlib
import os

argparser = argparse.ArgumentParser(prog="lo_updater", description="A tool for managing official LibreOffice installation on Debian.", epilog="GitHub project page: https://github.com/TheNooB2706/lo_updater")

operation = argparser.add_mutually_exclusive_group()
operation.add_argument("--check-only", "-c", help="Only check if there is update available.", action="store_true")
operation.add_argument("--download-only", help="Skip removal of old version and installation process, only download if there is newer version.", action="store_true")
operation.add_argument("--remove-only", help="Remove existing installation of LibreOffice.", action="store_true")
operation.add_argument("--install-only", help="Install downloaded installation archive. Take path to the archive as argument.", metavar="ARCHIVE_FILE", type=pathlib.Path)

argparser.add_argument("--use-latest-version", help="Update to the latest version instead of prompting which version to download if there are multiple new versions.", action="store_true")
argparser.add_argument("--dry-run", help="", default=False, action="store_true")

argparser.add_argument("--dl-dir", "-d", help="Use custom directory for downloading packages.", default=None, type=pathlib.Path)

args = argparser.parse_args()
#print(args) #TODO Remove debug print

if args.dl_dir is not None:
    updater.FILE_SAVE_LOCATION = str(args.dl_dir.absolute()) + "/"

if args.install_only is not None:
    if not args.install_only.exists():
        argparser.error(f"The provided archive {args.install_only.absolute()} does not exist.")
    else:
        updater.FILE_SAVE_LOCATION = str(args.install_only.parent.absolute()) + "/"

# Generic functions

def print_list(iterable, tabstop=0, sep=")"):
    for i in range(len(iterable)):
        print('\t'*tabstop+f"{i+1}{sep} {iterable[i]}")

def print_installed_version_list(updaterobj: updater.Updater):
    if updaterobj.installed:
        if updaterobj.multiple_installation:
            print("The following versions have been installed:")
            print_list(updaterobj.installed_version, tabstop=1)
        else:
            print(f"Version {updaterobj.installed_version[0]} is installed.")
    else:
        print("LibreOffice is not installed.")

def print_update_version_list(updaterobj: updater.Updater):
    if updaterobj.update_available:
        print("The following new versions are found: ")
        print_list(updaterobj.versions, tabstop=1)
    else:
        print("No available updates found.")

def print_version_list(updaterobj: updater.Updater):
    print_installed_version_list(updaterobj)
    print_update_version_list(updaterobj)

def prompt_selection(prompt, valid_selections, default=None):
    if len(valid_selections) == 0:
        return None
    selection = None
    str_valid_selection = [str(i) for i in valid_selections]
    if default is None:
        prompt_string = f"{prompt} [{'/'.join(str_valid_selection)}]: "
    else:
        prompt_string = f"{prompt} [{'/'.join(str_valid_selection)}] (default: {default}): "
    while selection is None:
        selection = input(prompt_string)
        if selection not in str_valid_selection:
            if selection == "":
                selection = default
            else:
                selection = None
                print("Invalid option selected, re-enter your choice.")
    return selection

def rename_old_file(filepath: pathlib.Path):
    i = 1
    target = filepath.parent / (filepath.name + f".{i}")
    while target.exists():
        i += 1
        target = filepath.parent / (filepath.name + f".{i}")
    return filepath.rename(target)

def check_old_leftover_file():
    extracted_path = pathlib.Path(updater.FILE_SAVE_LOCATION+"DEBS")
    if extracted_path.exists():
        print("Old extracted archive folder exists, renaming old folder...")
        oldfile = rename_old_file(extracted_path)
        print(f"Renamed {extracted_path.absolute()} to {oldfile.absolute()}.")

# Process function

def check_and_print_update(lo_updater):
    lo_updater.check_update()
    print_version_list(lo_updater)

def download_process(lo_updater, args):
    if args.use_latest_version:
        selected_version = len(lo_updater.versions)
    else:
        selected_version = prompt_selection("Select version to download", range(1,len(lo_updater.versions)+1), default=len(lo_updater.versions))
    if selected_version is not None:
        selected_version = int(selected_version)
        print(f"LibreOffice version {lo_updater.versions[selected_version-1].public} will be downloaded to {updater.FILE_SAVE_LOCATION}\n")
        lo_updater.set_install_version(lo_updater.versions[selected_version-1])
        
        while True:
            try:
                lo_updater.download_debs(dry_run=args.dry_run)
                return
            except updater.ChecksumMismatch as e:
                print(f"Archive downloaded with mismatched checksum ({e.downloaded_checksum} instead of {e.expected_checksum})")
                retry = prompt_selection("Redownload archive?", ["y", "n"], default="y")
                if retry == "n":
                    raise updater.ChecksumMismatch(e.expected_checksum, e.downloaded_checksum)

def removal_process(lo_updater, args):
    print_installed_version_list(lo_updater)
    if lo_updater.multiple_installation:
        version_selection = [i for i in range(1, len(lo_updater.installed_version)+1)]
        version_selection.append("skip")
        selected_version = prompt_selection("Select version to remove", version_selection)
        if selected_version == "skip":
            selected_version = None
        else:
            selected_version = int(selected_version)
            selected_version = lo_updater.installed_version[selected_version-1]
    elif lo_updater.installed:
        remove_confirm = prompt_selection("Are you sure you want to continue with the removal?", ["y","n"], default="n")
        if remove_confirm == "y":
            selected_version = lo_updater.installed_version[0]
        else:
            selected_version = None
    else:
        selected_version = None
        print("Skipping removal step.\n")
    if selected_version is not None:
        remove_version = f"{selected_version.major}.{selected_version.minor}"
        lo_updater.remove_installed(remove_version, dry_run=args.dry_run)

def install_process(lo_updater, args):
    if args.install_only:
        dry_run_extraction = args.dry_run
        if args.dry_run:
            print("You have enabled dry run option. Do you want to extract the archive to the disk? \
Extracting it allows you to dry run the dpkg installation command. If you choose to not extract, the simulation will only run until listing the content of the archive.")
            extract_even_with_dry_run = prompt_selection("Extract archive for real?", ["y","n"], default="n")
            if extract_even_with_dry_run == "y":
                check_old_leftover_file()
                dry_run_extraction = False
        else:
            check_old_leftover_file()
        print("Extracting installation archive...\n")
        lo_updater.extract_package(path=args.install_only.absolute(), dry_run=dry_run_extraction)
        if not dry_run_extraction:
            print("\nInstalling packages...\n")
            lo_updater.install_package(dry_run=args.dry_run)
    else:
        if not args.dry_run:
            check_old_leftover_file()
            print("Extracting installation archive...\n")
            lo_updater.extract_package()
            print("\nInstalling packages...\n")
            lo_updater.install_package()
        else:
            print("Dry run is enabled, skipping extraction and installation since archive is not downloaded.")

lo_updater = updater.Updater(no_check_update=True, dry_run=args.dry_run)

if args.check_only:
    check_and_print_update(lo_updater)
elif args.download_only:
    check_and_print_update(lo_updater)
    try:
        download_process(lo_updater, args)
    except updater.ChecksumMismatch:
        print("Archive download failed. Quitting.")
elif args.remove_only:
    removal_process(lo_updater, args)
elif args.install_only:
    install_process(lo_updater, args)
else:
    check_and_print_update(lo_updater)
    if lo_updater.update_available:
        try:
            download_process(lo_updater, args)
        except updater.ChecksumMismatch:
            print("Archive download failed. Quitting.")
        removal_process(lo_updater, args)
        install_process(lo_updater, args)