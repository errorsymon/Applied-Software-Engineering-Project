import sqlite3
import threading
from datetime import datetime
from config import DATABASE_NAME

class MetadataDatabase:
    def __init__(self):
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False, timeout=30)
        self._init_db()

    def _init_db(self):
        with self.lock:
            # Creating the exact 5 tables required by the validator spec
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS PROJECTS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repository_id INTEGER,
                    repository_url TEXT,
                    project_url TEXT,
                    title TEXT,
                    description TEXT,
                    download_date TEXT,
                    download_repository_folder TEXT,
                    download_project_folder TEXT,
                    download_method TEXT
                );
                CREATE TABLE IF NOT EXISTS FILES (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    file_name TEXT,
                    file_type TEXT,
                    status TEXT
                );
                CREATE TABLE IF NOT EXISTS KEYWORDS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    keyword TEXT
                );
                CREATE TABLE IF NOT EXISTS PERSON_ROLE (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    name TEXT,
                    role TEXT
                );
                CREATE TABLE IF NOT EXISTS LICENSES (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    license TEXT
                );
            """)
            self.conn.commit()

    def get_or_create_project(self, repo, project_url, title, description, dl_repo_folder, dl_proj_folder):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT id FROM PROJECTS WHERE project_url=?", (project_url,))
            row = cur.fetchone()
            if row:
                return row[0]
            
            dl_date = datetime.now().isoformat()
            cur.execute("""
                INSERT INTO PROJECTS (
                    repository_id, repository_url, project_url, title, description, 
                    download_date, download_repository_folder, download_project_folder, download_method
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (1, repo, project_url, title, description, dl_date, dl_repo_folder, dl_proj_folder, "API"))
            self.conn.commit()
            return cur.lastrowid

    def insert_file(self, project_id, file_name, file_type, status):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT id FROM FILES WHERE project_id=? AND file_name=?", (project_id, file_name))
            if not cur.fetchone():
                cur.execute("INSERT INTO FILES (project_id, file_name, file_type, status) VALUES (?, ?, ?, ?)",
                            (project_id, file_name, file_type, status))
                self.conn.commit()

    def add_person(self, project_id, name, role="AUTHOR"):
        if not name: return
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT id FROM PERSON_ROLE WHERE project_id=? AND name=? AND role=?", (project_id, name, role))
            if not cur.fetchone():
                cur.execute("INSERT INTO PERSON_ROLE (project_id, name, role) VALUES (?, ?, ?)", (project_id, name, role))
                self.conn.commit()

    def add_license(self, project_id, license_name):
        if not license_name: return
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT id FROM LICENSES WHERE project_id=? AND license=?", (project_id, license_name))
            if not cur.fetchone():
                cur.execute("INSERT INTO LICENSES (project_id, license) VALUES (?, ?)", (project_id, license_name))
                self.conn.commit()
                
    def add_keyword(self, project_id, keyword):
        if not keyword: return
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT id FROM KEYWORDS WHERE project_id=? AND keyword=?", (project_id, keyword))
            if not cur.fetchone():
                cur.execute("INSERT INTO KEYWORDS (project_id, keyword) VALUES (?, ?)", (project_id, keyword))
                self.conn.commit()
                
    def get_unclassified_projects(self):
        with self.lock:
            cur = self.conn.cursor()
            # Fetch projects that haven't been tagged by the classifier yet
            cur.execute('''
                SELECT id, title, description FROM PROJECTS 
                WHERE id NOT IN (SELECT project_id FROM KEYWORDS WHERE keyword LIKE 'ISIC:%')
            ''')
            return cur.fetchall()

    def exists(self, url):
        # We handle exists logic inside the downloader now based on file names
        return False
        
    def count(self):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM FILES WHERE status='SUCCEEDED'")
            return cur.fetchone()[0]
            
    def close(self):
        self.conn.close()
