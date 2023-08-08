import updater
import argparse
import sys
import pathlib

argparser = argparse.ArgumentParser(epilog="GitHub project page: ")

operation = argparser.add_mutually_exclusive_group()
operation.add_argument("--check-only", "-c", help="Only check if there is update available.", action="store_true")
operation.add_argument("--download-only", help="Skip removal of old version and installation process, only download if there is newer version.", action="store_true")
operation.add_argument("--remove-only", help="Remove existing installation of LibreOffice.", action="store_true")

argparser.add_argument("--use-latest-version", help="Update to the latest version instead of prompting which version to download if there are multiple new versions.", action="store_true")
argparser.add_argument("--dry-run", help="", default=False, action="store_true")

argparser.add_argument("--dl-dir", "-d", help="Use custom directory for downloading packages.", default=None, type=pathlib.Path)

args = argparser.parse_args()
print(args) #TODO Remove debug print

if args.dl_dir is not None:
    updater.FILE_SAVE_LOCATION = str(args.dl_dir.absolute()) + "/"

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
        lo_updater.download_debs(dry_run=args.dry_run)

def removal_process(lo_updater, args):
    print_installed_version_list(lo_updater)
    if lo_updater.multiple_installation:
        selected_version = prompt_selection("Select version to remove", range(1, len(lo_updater.installed_version)+1))
    elif lo_updater.installed:
        remove_confirm = prompt_selection("Are you sure you want to continue with the removal?", ["y","n"], default="n")
        if remove_confirm == "y":
            selected_version = lo_updater.installed_version[0]
        else:
            selected_version = None
    else:
        selected_version = None
    if selected_version is not None:
        remove_version = f"{selected_version.major}.{selected_version.minor}"
        lo_updater.remove_installed(remove_version, dry_run=args.dry_run)

lo_updater = updater.Updater(no_check_update=True, dry_run=args.dry_run)

if args.check_only:
    check_and_print_update(lo_updater)
elif args.download_only:
    check_and_print_update(lo_updater)
    download_process(lo_updater, args)
elif args.remove_only:
    removal_process(lo_updater, args)
