import requests
import subprocess
import re
from bs4 import BeautifulSoup as bs
from packaging import version

STABLE_CHECK_URL = "https://download.documentfoundation.org/libreoffice/stable/"

class Updater:
    def __init__(self, no_check_update=False):
        self.multiple_installation = False
        self.installed = False
        self.update_available = False
        
        if not no_check_update:
            versions = self.contents_to_version(self.fetch_page(STABLE_CHECK_URL))
            self.latest_version = max(versions)
        else:
            self.latest_version = version.parse("0")
        self.installed_version = self.check_current_version()
        if len(self.installed_version) > 1:
            self.multiple_installation = True
            self.installed = True
        elif len(self.installed_version) == 1:
            self.installed = True
            
        if max(self.installed_version) < self.latest_version:
            self.update_available = True

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
    def remove_installed(target_version, dry_run=False):
        command = ["apt", "remove", f"libreoffice{target_version}*", f"libobasis{target_version}*"]
        if dry_run:
            command.append("--dry-run")
        
        execution = subprocess.run(command, check=True)
        execution.check_returncode()
    
    
if __name__ == "__main__":
    updater = Updater(no_check_update=True)
    print(updater.latest_version)
    print(updater.installed_version)
    print(updater.multiple_installation)
    print(updater.update_available)
    print(updater.installed)
    updater.remove_installed("7.5", dry_run=True)
