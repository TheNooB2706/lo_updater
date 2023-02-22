import requests
from bs4 import BeautifulSoup as bs
from packaging import version

STABLE_CHECK_URL = "https://download.documentfoundation.org/libreoffice/stable/"

class Updater:
    def __init__(self):
        versions = self.contents_to_version(self.fetch_page(STABLE_CHECK_URL))
        self.latest_version = max(versions)

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
    
    
if __name__ == "__main__":
    updater = Updater()
    print(updater.latest_version)
