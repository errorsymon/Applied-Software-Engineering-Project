import sqlite3
import time
from config import DATABASE_NAME


class MetadataDatabase:

    def __init__(self):

        # Create connection with timeout to reduce locking problems
        self.conn = sqlite3.connect(
            DATABASE_NAME,
            check_same_thread=False,
            timeout=30
        )

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS qda_files(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            timestamp TEXT,
            repository TEXT,
            filename TEXT,
            local_dir TEXT,
            license TEXT,
            uploader TEXT,
            file_type TEXT,
            file_hash TEXT
        )
        """)

        self.conn.commit()

    # -------------------------
    # Check if URL already exists
    # -------------------------

    def exists(self, url):

        cur = self.conn.cursor()

        cur.execute(
            "SELECT 1 FROM qda_files WHERE url=?",
            (url,)
        )

        return cur.fetchone() is not None

    # -------------------------
    # Insert metadata
    # -------------------------

    def insert(self, data):

        for attempt in range(5):

            try:

                with self.conn:

                    self.conn.execute("""
                    INSERT OR IGNORE INTO qda_files
                    (
                        url,
                        timestamp,
                        repository,
                        filename,
                        local_dir,
                        license,
                        uploader,
                        file_type,
                        file_hash
                    )
                    VALUES(?,?,?,?,?,?,?,?,?)
                    """, data)

                return

            except sqlite3.OperationalError as e:

                if "locked" in str(e):

                    time.sleep(1)

                else:
                    raise e

    # -------------------------
    # Count total files
    # -------------------------

    def count(self):

        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM qda_files")

        return cur.fetchone()[0]

    # -------------------------
    # Export metadata to CSV
    # -------------------------

    def export_csv(self, output_file="metadata_export.csv"):

        import csv

        cur = self.conn.cursor()

        cur.execute("SELECT * FROM qda_files")

        rows = cur.fetchall()

        headers = [description[0] for description in cur.description]

        with open(output_file, "w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            writer.writerow(headers)

            writer.writerows(rows)

    # -------------------------
    # Close connection
    # -------------------------

    def close(self):

        self.conn.close()