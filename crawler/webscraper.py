import sqlite3
import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.createPeopleTables()

    def createPeopleTables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS actors (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                avatar TEXT,
                bio TEXT,
                date_of_birth TEXT,
                date_of_death TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS writers (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                avatar TEXT,
                bio TEXT,
                date_of_birth TEXT,
                date_of_death TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS directors (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                avatar TEXT,
                bio TEXT,
                date_of_birth TEXT,
                date_of_death TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie_actors (
                movie_id INTEGER,
                actor_id INTEGER,
                FOREIGN KEY (movie_id) REFERENCES filemetadata(file_id),
                FOREIGN KEY (actor_id) REFERENCES actors(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie_writers (
                movie_id INTEGER,
                writer_id INTEGER,
                FOREIGN KEY (movie_id) REFERENCES filemetadata(file_id),
                FOREIGN KEY (writer_id) REFERENCES writers(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie_directors (
                movie_id INTEGER,
                director_id INTEGER,
                FOREIGN KEY (movie_id) REFERENCES filemetadata(file_id),
                FOREIGN KEY (director_id) REFERENCES directors(id)
            )
        """)
        self.conn.commit()

    def fetchMetadata(self):
        self.cursor.execute("SELECT file_id, actors, writer, director FROM filemetadata")
        return self.cursor.fetchall()

    def classifyMetadata(self):
        metadata = self.fetchMetadata()
        for file_id, actors, writers, directors in metadata:
            self.classifyActors(file_id, actors)
            self.classifyWriters(file_id, writers)
            self.classifyDirectors(file_id, directors)
        self.conn.commit()

    def classifyActors(self, file_id, actors):
        for actor in actors.split(', '):
            actor = actor.strip()
            self.cursor.execute("INSERT OR IGNORE INTO actors (name) VALUES (?)", (actor,))
            self.cursor.execute("SELECT id, avatar, bio FROM actors WHERE name = ?", (actor,))
            result = self.cursor.fetchone()
            
            if result:
                actor_id, avatar, bio = result
                self.cursor.execute("SELECT 1 FROM movie_actors WHERE movie_id = ? AND actor_id = ?", (file_id, actor_id))
                if not self.cursor.fetchone():
                    self.cursor.execute("INSERT INTO movie_actors (movie_id, actor_id) VALUES (?, ?)", (file_id, actor_id))

                # Update only if details are missing
                if not avatar and not bio:
                    self.updatePersonDetails('actors', actor, actor_id)

    def classifyWriters(self, file_id, writers):
        for writer in writers.split(', '):
            writer = writer.strip()
            self.cursor.execute("INSERT OR IGNORE INTO writers (name) VALUES (?)", (writer,))
            self.cursor.execute("SELECT id, avatar, bio FROM writers WHERE name = ?", (writer,))
            result = self.cursor.fetchone()

            if result:
                writer_id, avatar, bio = result
                self.cursor.execute("SELECT 1 FROM movie_writers WHERE movie_id = ? AND writer_id = ?", (file_id, writer_id))
                if not self.cursor.fetchone():
                    self.cursor.execute("INSERT INTO movie_writers (movie_id, writer_id) VALUES (?, ?)", (file_id, writer_id))

                if not avatar and not bio:
                    self.updatePersonDetails('writers', writer, writer_id)

    def classifyDirectors(self, file_id, directors):
        for director in directors.split(', '):
            director = director.strip()
            self.cursor.execute("INSERT OR IGNORE INTO directors (name) VALUES (?)", (director,))
            self.cursor.execute("SELECT id, avatar, bio FROM directors WHERE name = ?", (director,))
            result = self.cursor.fetchone()

            if result:
                director_id, avatar, bio = result
                self.cursor.execute("SELECT 1 FROM movie_directors WHERE movie_id = ? AND director_id = ?", (file_id, director_id))
                if not self.cursor.fetchone():
                    self.cursor.execute("INSERT INTO movie_directors (movie_id, director_id) VALUES (?, ?)", (file_id, director_id))

                if not avatar and not bio:
                    self.updatePersonDetails('directors', director, director_id)

    def updatePersonDetails(self, table, name, person_id):
        url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        
        # Check if the Wikipedia page exists
        if response.status_code == 404:
            print(f"⚠️ Wikipedia page not found for: {name} ({url})")
            return  # Skip this person
        
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch Wikipedia page for {name} (Status: {response.status_code})")
            return  # Skip this person
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract avatar (check if infobox exists)
        avatar = None
        infobox = soup.find('table', {'class': 'infobox'})
        if infobox:
            img_tag = infobox.find('img')
            if img_tag and 'src' in img_tag.attrs:
                avatar = f"https:{img_tag['src']}"

        # Extract meaningful bio (skip empty paragraphs)
        bio = None
        for p in soup.select('.mw-parser-output > p'):
            text = p.text.strip()
            if text:  # Skip empty or irrelevant paragraphs
                bio = text
                break

        # Extract dates
        date_of_birth = None
        date_of_death = None

        bday_span = soup.find('span', {'class': 'bday'})
        if bday_span:
            date_of_birth = bday_span.text

        death_span = soup.find('span', {'class': 'dday'}) or soup.find('time', {'datetime'})
        if death_span:
            date_of_death = death_span.text

        # Update database
        self.cursor.execute(f"""
            UPDATE {table} SET avatar = ?, bio = ?, date_of_birth = ?, date_of_death = ? WHERE id = ?
        """, (avatar, bio, date_of_birth, date_of_death, person_id))
        self.conn.commit()

        print(f"✔ Updated Wikipedia details for: {name}")

    def close(self):
        self.conn.close()
