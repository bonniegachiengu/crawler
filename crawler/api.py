import requests
import sqlite3
from .utils import fetch

class API:
    def __init__(self, url, apikey, dbpath='../classified.db'):
        self.url = url
        self.apikey = apikey
        self.dbpath = dbpath

    def collect(self):
        """Fetch file_id, title, and year from filedetails."""
        columns = ['file_id', 'title', 'year']
        table_title = 'filedetails'
        return fetch(columns, table_title)

    def search(self, file_id, title, year):
        """Search OMDb API for movie details."""
        # Fetch the correct title from the filedetails table
        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM filedetails WHERE file_id = ?", (file_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            title = result[0]

        params = {"t": title, "y": year, "apikey": self.apikey}
        response = requests.get(self.url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True':
                self.save(file_id, data)  # Link metadata to file_id
                print(f"Saved: {title} ({year})")
                return data
            else:
                print(f"Not Found: {title} ({year})")
        else:
            print(f"Error {response.status_code}: {title} ({year})")

        return None

    def save(self, file_id, data):
        """Save metadata into filemetadata, linking with filedetails.file_id."""
        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()

        # Fetch the correct title from the filedetails table
        cursor.execute("SELECT title FROM filedetails WHERE file_id = ?", (file_id,))
        result = cursor.fetchone()
        if result:
            title = result[0]
        else:
            title = data.get("Title")

        # Create filemetadata table if it does not exist
        self._create_filemetadata_table(cursor)

        # Extract IMDb and Rotten Tomatoes ratings
        imdb_rating = None
        rotten_tomatoes = None
        for rating in data.get("Ratings", []):
            if rating["Source"] == "Internet Movie Database":
                imdb_rating = rating["Value"]
            elif rating["Source"] == "Rotten Tomatoes":
                rotten_tomatoes = rating["Value"]

        # Insert or update metadata
        cursor.execute("""
            INSERT OR REPLACE INTO filemetadata (
                file_id, imdbID, title, year, rated, released, runtime, genre, 
                director, writer, actors, plot, language, country, awards, 
                poster, imdbRating, imdbVotes, rottenTomatoes, type, boxoffice
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            file_id, data.get("imdbID"), title, data.get("Year"),
            data.get("Rated"), data.get("Released"), data.get("Runtime"),
            data.get("Genre"), data.get("Director"), data.get("Writer"),
            data.get("Actors"), data.get("Plot"), data.get("Language"),
            data.get("Country"), data.get("Awards"), data.get("Poster"),
            imdb_rating, data.get("imdbVotes"), rotten_tomatoes,
            data.get("Type"), data.get("BoxOffice")
        ))

        conn.commit()
        conn.close()

    def is_processed(self, file_id):
        """Check if the file has already been processed."""
        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()
        self._create_filemetadata_table(cursor)
        cursor.execute("SELECT 1 FROM filemetadata WHERE file_id = ?", (file_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def _create_filemetadata_table(self, cursor):
        """Create filemetadata table if it does not exist."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filemetadata (
                file_id INTEGER PRIMARY KEY,  
                imdbID TEXT UNIQUE,
                title TEXT,
                year TEXT,
                rated TEXT,
                released TEXT,
                runtime TEXT,
                genre TEXT,
                director TEXT,
                writer TEXT,
                actors TEXT,
                plot TEXT,
                language TEXT,
                country TEXT,
                awards TEXT,
                poster TEXT,
                imdbRating TEXT,
                imdbVotes TEXT,
                rottenTomatoes TEXT,
                type TEXT,
                boxoffice TEXT,
                FOREIGN KEY (file_id) REFERENCES filedetails(file_id) ON DELETE CASCADE
            )
        """)
