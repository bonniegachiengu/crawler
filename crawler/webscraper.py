import sqlite3

class WebScraper:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS actors (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS writers (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS directors (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
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

    def fetch_metadata(self):
        self.cursor.execute("SELECT file_id, actors, writer, director FROM filemetadata")
        return self.cursor.fetchall()

    def classify_metadata(self):
        metadata = self.fetch_metadata()
        for file_id, actors, writers, directors in metadata:
            self._classify_actors(file_id, actors)
            self._classify_writers(file_id, writers)
            self._classify_directors(file_id, directors)
        self.conn.commit()

    def _classify_actors(self, file_id, actors):
        for actor in actors.split(', '):
            actor = actor.strip()
            self.cursor.execute("INSERT OR IGNORE INTO actors (name) VALUES (?)", (actor,))
            self.cursor.execute("SELECT id FROM actors WHERE name = ?", (actor,))
            actor_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO movie_actors (movie_id, actor_id) VALUES (?, ?)", (file_id, actor_id))

    def _classify_writers(self, file_id, writers):
        for writer in writers.split(', '):
            writer = writer.strip()
            self.cursor.execute("INSERT OR IGNORE INTO writers (name) VALUES (?)", (writer,))
            self.cursor.execute("SELECT id FROM writers WHERE name = ?", (writer,))
            writer_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO movie_writers (movie_id, writer_id) VALUES (?, ?)", (file_id, writer_id))

    def _classify_directors(self, file_id, directors):
        for director in directors.split(', '):
            director = director.strip()
            self.cursor.execute("INSERT OR IGNORE INTO directors (name) VALUES (?)", (director,))
            self.cursor.execute("SELECT id FROM directors WHERE name = ?", (director,))
            director_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO movie_directors (movie_id, director_id) VALUES (?, ?)", (file_id, director_id))

    def close(self):
        self.conn.close()
