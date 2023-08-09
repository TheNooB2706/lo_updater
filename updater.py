import requests
import subprocess
import re
import pathlib
import os
from bs4 import BeautifulSoup as bs
from packaging import version

STABLE_CHECK_URL = "https://download.documentfoundation.org/libreoffice/stable/"
FILE_SAVE_LOCATION = str(pathlib.Path("~/Downloads/libreoffice_updater/").expanduser())+"/"

class Updater:
    def __init__(self, no_check_update=False, dry_run=False):
        self.multiple_installation = False
        self.installed = False
        self.update_available = False
        
        self.check_update(no_check_update=no_check_update)

        self.create_dl_folder(dry_run=dry_run)

    def check_update(self, no_check_update=False):
        if not no_check_update:
            self.web_versions = self.contents_to_version(self.fetch_page(STABLE_CHECK_URL))
            self.latest_version = max(self.web_versions)
        else:
            self.latest_version = version.parse("0")
            self.versions = []
        self.installed_version = self.check_current_version()
        if len(self.installed_version) > 1:
            self.multiple_installation = True
            self.installed = True
        elif len(self.installed_version) == 1:
            self.installed = True
            
        if max(self.installed_version) < self.latest_version:
            self.update_available = True
            self.versions = [i for i in self.web_versions if i>max(self.installed_version)]

    @staticmethod
    def create_dl_folder(dry_run=False):
        if not dry_run:
            if not os.path.exists(FILE_SAVE_LOCATION):
                os.makedirs(FILE_SAVE_LOCATION)

    @staticmethod
    def fetch_page(url):
        dlpage = requests.get(url)

        soup = bs(dlpage.text, "html.parser")
        table = soup.find("table")
        rows = table.findChildren("tr")

        contents = rows[3:-1]
        contents = [i.find("a").decode_contents() for i in contents]

        return contents
    
    @staticmethod
    def contents_to_version(contents):
        return [version.parse(i[:-1]) for i in contents]
    
    @staticmethod
    def check_current_version():
        pattern = re.compile("^libreoffice\d+\.\d+$")
        
        command = ["dpkg-query", "-W", "libreoffice*"]
        execution = subprocess.run(command, capture_output=True)
        output = execution.stdout.decode()
        output = [i.split("\t") for i in output.split("\n")]
        
        installed = [i[1] for i in output if pattern.match(i[0])]
        return [version.parse(i) for i in installed]
    
    @staticmethod
    def remove_installed(target_version: str, dry_run=False):
        command = ["sudo", "apt", "remove", f"libreoffice{target_version}*", f"libobasis{target_version}*"]
        if dry_run:
            command.append("--dry-run")
        
        execution = subprocess.run(command, check=True)
        execution.check_returncode()
    
    def download_debs(self, no_check_update=False, dry_run=False):
        if not no_check_update:
            if self.update_available:
                dllink = f"{STABLE_CHECK_URL}/{self.latest_version.public}/deb/x86_64/LibreOffice_{self.latest_version.public}_Linux_x86-64_deb.tar.gz"
            else:
                return "Already at latest version!"
        else:
            dllink = f"{STABLE_CHECK_URL}/{self.latest_version.public}/deb/x86_64/LibreOffice_{self.latest_version.public}_Linux_x86-64_deb.tar.gz"
            
        sha256hash = self.get_sha256_hash(dllink)
        
        if not dry_run:
            wget_command = ["wget", dllink, "-P", FILE_SAVE_LOCATION]
            dl_execution = subprocess.run(wget_command, check=True)
            dl_execution.check_returncode()
            
            downloaded_hash = subprocess.run(["sha256sum", FILE_SAVE_LOCATION+f"LibreOffice_{self.latest_version.public}_Linux_x86-64_deb.tar.gz"], capture_output=True).stdout.decode().split()[0]
            
            if sha256hash == downloaded_hash:
                return "Download complete"
            else:
                raise ChecksumMismatch(sha256hash, downloaded_hash)
        else:
            wget_command = ["wget", "--spider", dllink]
            dl_execution = subprocess.run(wget_command, check=True)
            return "Download complete"
    
    @staticmethod
    def get_sha256_hash(download_link):
        hashlink = download_link + ".sha256"
        hashcontent = requests.get(hashlink)
        sha256hash = hashcontent.text.split()[0]
        return sha256hash
    
    def extract_package(self, path:str=None, dry_run=False):
        if dry_run:
            command = ["tar", "-tf"]
            if path is None:
                command.append(FILE_SAVE_LOCATION+f"LibreOffice_{self.latest_version.public}_Linux_x86-64_deb.tar.gz")
            else:
                command.append(path)
        else:
            command = ["tar", "zxvf"]
            if path is None:
                command += [FILE_SAVE_LOCATION+f"LibreOffice_{self.latest_version.public}_Linux_x86-64_deb.tar.gz", "-C", FILE_SAVE_LOCATION, "--strip-components=1"]
            else:
                command += [path, "-C", FILE_SAVE_LOCATION, "--strip-components=1"]
        
        extract_execution = subprocess.run(command, check=True)
        extract_execution.check_returncode()
        
    def install_package(self, dry_run=False):
        command = ["sudo", "dpkg", "-i", FILE_SAVE_LOCATION+"DEBS/*.deb"]
        
        if dry_run:
            command.insert(2, "--dry-run")
            
        command = " ".join(command)
            
        install_execution = subprocess.run(command, check=True, shell=True)
        install_execution.check_returncode()

    def set_install_version(self, version):
        self.latest_version = version

# Error

class ChecksumMismatch(Exception):
    """Exception raised for error in downloaded archive"""
    def __init__(self, expected_checksum, downloaded_checksum):
        self.expected_checksum = expected_checksum
        self.downloaded_checksum = downloaded_checksum
        super().__init__(f"Expected {expected_checksum}, got {downloaded_checksum}.")
    
if __name__ == "__main__":
    # updater = Updater()
    # print(updater.update_available)
    # updater.latest_version = version.parse("7.5.5")
    # updater.download_debs(no_check_update=True, dry_run=True)
    #updater.latest_version = version.parse("7.5.0")
    #updater.remove_installed("7.5", dry_run=True)
    #updater.extract_package(dry_run=True)
    #updater.install_package(dry_run=True)
    raise ChecksumMismatch("abcd","efgh")
