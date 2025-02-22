"""
Crawler Package

This package provides a Crawler class that integrates data from an API and a web scraper.
It fetches movie data from the API and people data from the web scraper, and populates a database with this information.

Usage:
    from crawler.crawler import Crawler

    def main():
        dbpath = "../classified.db"  # Path to your SQLite database
        api_url = "http://www.omdbapi.com/"  # OMDb API URL
        api_key = "your_api_key_here"  # Your OMDb API key
        directory = r'E:\Films\Movies\Adventure\Comics'  # Directory to search for media files
        extensions = ('mp4', 'mkv', 'avi')  # File extensions to look for

        # Create an instance of the Crawler class
        crawler = Crawler(dbpath, api_url, api_key, directory, extensions)
        
        # Run the crawl method to start the crawling process
        crawler.crawl()

    if __name__ == "__main__":
        main()
"""

from finder.finder import Finder
from .webscraper import WebScraper
from .api import API
import sqlite3
import os

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
        # Run Finder to populate the database with file details
        self.finder.run(directory=self.directory, extensions=self.extensions)

        # Get the list of processed file IDs
        processed_file_ids = self.get_processed_file_ids()

        # Collect movies from the API
        movies = self.api.collect()

        # Filter out processed movies
        unprocessed_movies = [movie for movie in movies if movie[0] not in processed_file_ids]

        # Process unprocessed movies using the API
        for file_id, title, year in unprocessed_movies:
            self.api.search(file_id, title, year)

        # Classify metadata using the WebScraper
        self.scraper.classifyMetadata()
        self.scraper.close()

    def get_processed_file_ids(self):
        """
        Fetch the list of file_ids that have already been processed.
        """
        if not os.path.exists(self.dbpath):
            print(f"Database not found at {self.dbpath}. Returning empty set of processed file IDs.")
            return set()

        try:
            conn = sqlite3.connect(self.dbpath)
            cursor = conn.cursor()

            # Check if the required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('filepaths', 'filedetails')")
            tables = {row[0] for row in cursor.fetchall()}
            if not {'filepaths', 'filedetails'}.issubset(tables):
                print("Required tables not found in the database. Returning empty set of processed file IDs.")
                return set()

            cursor.execute("SELECT file_id FROM filemetadata")
            processed_file_ids = {row[0] for row in cursor.fetchall()}
            conn.close()
            return processed_file_ids
        except sqlite3.Error as e:
            print(f"An error occurred while accessing the database: {e}")
            return set()

def main():
    dbpath = "classifier/classified.db"
    api_url = "http://www.omdbapi.com/"
    api_key = "1787320b"
    directory = r'E:\Films\Movies\Adventure\Comics'
    extensions = ('mp4', 'mkv', 'avi')

    crawler = Crawler(dbpath, api_url, api_key, directory, extensions)
    crawler.crawl()

if __name__ == "__main__":
    main()