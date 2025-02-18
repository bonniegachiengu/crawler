from finder.finder import Finder
from api import API
import sqlite3
from webscraper import WebScraper

finder = Finder()
api = API("http://www.omdbapi.com/", "1787320b")

# Run the Finder process with specified directory and extensions
finder.run(directory=r'E:\Films\Movies\New folder', extensions=('mp4', 'mkv', 'avi'))

# Collect all movies
movies = api.collect()

# Fetch and save details for each movie if not already processed
for file_id, title, year in movies:
    if not api.is_processed(file_id):
        api.search(file_id, title, year)

# Classify metadata
scraper = WebScraper(db_path='../classified.db')
scraper.classifyMetadata()
scraper.close()