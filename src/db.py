import sqlite3
import json

def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    def __init__(self):
        self.conn = sqlite3.connect("wikiracer.db", check_same_thread=False)
        self.create_tables()

    def create_tables(self):

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS paths (
                start_page TEXT NOT NULL,
                end_page TEXT NOT NULL,
                path TEXT NOT NULL,
                links TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                PRIMARY KEY (start_page, end_page)
            );
        """)

    def get_paths(self):
        # Retrieve all paths from the database
        paths = []
        cursor = self.conn.execute("""
            SELECT start_page, end_page, path, timestamp from paths;
        """)
        for row in cursor:
            paths.append({"start page": row[0], "end page": row[1], "path": row[2], "timestamp" : row[3]})
        return paths
    
    def create_path(self, start_page, end_page, path, links, timestamp):
        # Insert a new path into the database
        cursor = self.conn.execute("""
            INSERT INTO paths (start_page, end_page, path, links, timestamp)
            VALUES (?, ?, ?, ?, ?);
        """, (start_page, end_page, json.dumps(path), json.dumps(links), timestamp))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_path(self, start_page_title, end_page_title):
        cursor = self.conn.execute("""
                SELECT * FROM paths WHERE start_page = ? AND end_page = ?
                                """ , (start_page_title, end_page_title))
        result = cursor.fetchone()
        if result:
            column_names = [description[0] for description in cursor.description]
            return dict(zip(column_names, result))
        return None

