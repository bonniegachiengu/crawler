import sqlite3

class WebScraper:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def fetch_metadata(self):
        self.cursor.execute("SELECT file_id, actors, writers, directors FROM filemetadata")
        return self.cursor.fetchall()

    def classify_metadata(self):
        metadata = self.fetch_metadata()
        for file_id, actors, writers, directors in metadata:
            self.classify_actors(file_id, actors)
            self.classify_writers(file_id, writers)
            self.classify_directors(file_id, directors)

    def classify_actors(self, file_id, actors):
        for actor in actors.split(','):
            actor = actor.strip()
            self.cursor.execute("INSERT OR IGNORE INTO actors (name) VALUES (?)", (actor,))
            self.cursor.execute("INSERT INTO movie_actors (movie_id, actor_id) VALUES (?, (SELECT id FROM actors WHERE name=?))", (file_id, actor))

    def classify_writers(self, file_id, writers):
        for writer in writers.split(','):
            writer = writer.strip()
            self.cursor.execute("INSERT OR IGNORE INTO writers (name) VALUES (?)", (writer,))
            self.cursor.execute("INSERT INTO movie_writers (movie_id, writer_id) VALUES (?, (SELECT id FROM writers WHERE name=?))", (file_id, writer))

    def classify_directors(self, file_id, directors):
        for director in directors.split(','):
            director = director.strip()
            self.cursor.execute("INSERT OR IGNORE INTO directors (name) VALUES (?)", (director,))
            self.cursor.execute("INSERT INTO movie_directors (movie_id, director_id) VALUES (?, (SELECT id FROM directors WHERE name=?))", (file_id, director))

    def close(self):
        self.conn.commit()
        self.conn.close()
