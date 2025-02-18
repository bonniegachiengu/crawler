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
            self.cursor.execute("SELECT id FROM actors WHERE name = ?", (actor,))
            actor_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO movie_actors (movie_id, actor_id) VALUES (?, ?)", (file_id, actor_id))
            self.updatePersonDetails('actors', actor, actor_id)

    def classifyWriters(self, file_id, writers):
        for writer in writers.split(', '):
            writer = writer.strip()
            self.cursor.execute("INSERT OR IGNORE INTO writers (name) VALUES (?)", (writer,))
            self.cursor.execute("SELECT id FROM writers WHERE name = ?", (writer,))
            writer_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO movie_writers (movie_id, writer_id) VALUES (?, ?)", (file_id, writer_id))
            self.updatePersonDetails('writers', writer, writer_id)

    def classifyDirectors(self, file_id, directors):
        for director in directors.split(', '):
            director = director.strip()
            self.cursor.execute("INSERT OR IGNORE INTO directors (name) VALUES (?)", (director,))
            self.cursor.execute("SELECT id FROM directors WHERE name = ?", (director,))
            director_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO movie_directors (movie_id, director_id) VALUES (?, ?)", (file_id, director_id))
            self.updatePersonDetails('directors', director, director_id)

    def updatePersonDetails(self, table, name, person_id):
        url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            avatar = soup.find('table', {'class': 'infobox'}).find('img')['src'] if soup.find('table', {'class': 'infobox'}) and soup.find('table', {'class': 'infobox'}).find('img') else None
            bio = soup.find('div', {'class': 'mw-parser-output'}).find('p').text if soup.find('div', {'class': 'mw-parser-output'}) and soup.find('div', {'class': 'mw-parser-output'}).find('p') else None
            date_of_birth = soup.find('span', {'class': 'bday'}).text if soup.find('span', {'class': 'bday'}) else None
            date_of_death = soup.find('span', {'class': 'dday'}).text if soup.find('span', {'class': 'dday'}) else None
            self.cursor.execute(f"""
                UPDATE {table} SET avatar = ?, bio = ?, date_of_birth = ?, date_of_death = ? WHERE id = ?
            """, (avatar, bio, date_of_birth, date_of_death, person_id))
            self.conn.commit()

    def close(self):
        self.conn.close()
