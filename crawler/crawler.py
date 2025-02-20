from finder.finder import Finder
from webscraper import WebScraper
from api import API

class Crawler:
    """
    Crawler class brings together data from the API and web scraper.
    From the API, it gets the movie data and from the web scraper it gets the people data.
    """

    def __init__(self, dbpath, api_url, api_key, directory, extensions):
        self.dbpath = dbpath
        self.api = API(api_url, api_key, dbpath=dbpath)
        self.scraper = WebScraper(dbpath)
        self.finder = Finder()
        self.directory = directory
        self.extensions = extensions

    def crawl(self):
        """
        Crawl uses Finder to populate the database with file details.
        Then it uses WebScraper to populate the people tables.
        Finally, it uses API to populate the movie tables.
        """
        self.finder.run(directory=self.directory, extensions=self.extensions)

        movies = self.api.collect()

        for file_id, title, year in movies:
            if not self.api.is_processed(file_id):
                self.api.search(file_id, title, year)
        
        self.scraper.classifyMetadata()
        self.scraper.close()

def main():
    dbpath = "../classified.db"
    api_url = "http://www.omdbapi.com/"
    api_key = "1787320b"
    directory = r'E:\Films\Movies\Adventure\Comics'
    extensions = ('mp4', 'mkv', 'avi')

    crawler = Crawler(dbpath, api_url, api_key, directory, extensions)
    crawler.crawl()

if __name__ == "__main__":
    main()