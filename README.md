QDArchive Seeding Project 
Student: Symon Islam

Student ID: 23088045

Course: Applied Software Engineering

Supervisor: Prof. Dr. Dirk Riehle

University: Friedrich-Alexander-Universität Erlangen-Nürnberg (FAU)

Project Overview
This project is part of the Seeding QDArchive initiative.

The goal is to automatically collect qualitative research datasets from public repositories, store them in a structured database, and systematically classify them using the ISIC Rev. 5 taxonomy.

The system:

Searches repositories using hyper-specific qualitative and QDA-software queries

Bypasses bot-detection and gracefully handles API rate limits

Downloads available dataset files (QDA and primary files) concurrently

Extracts metadata (descriptions) for automated text classification

Categorizes data into ISIC Rev. 5 Divisions

Reconstructs fragmented downloads into logical project folders

This project provides a robust, classified foundation for QDArchive, a platform for sharing qualitative research data.

Project Goal
Discover qualitative datasets across diverse academic fields

Download QDA formats and associated media/text files

Extract rich metadata (abstracts, titles, descriptions)

Store everything in a thread-safe SQLite database

Classify datasets automatically using ISIC Rev. 5 standards

Reconstruct datasets locally for QDArchive ingestion

Assigned Repositories
#	Repository	URL	Method
1	SIKT (Norwegian Agency for Shared Services in Education and Research)	https://dataverse.no/	Dataverse API (Deep Pagination)
2	FSD (Finnish Social Science Data Archive)	https://www.fsd.tuni.fi/en/	HTML Crawling + DDI XML
Search Strategy
General Methodological Queries
qualitative interview

ethnography

focus group transcript

grounded theory

participant observation

oral history

QDA-Specific & Tool-Targeted Queries
MAXQDA project / .mx24 / .mqda

NVivo research data / .nvpx

ATLAS.ti bundle / .atlproj

REFI-QDA export / .qdpx

These queries act as "bait" to detect datasets containing actual qualitative data analysis (QDA) software files.

Acquisition Approach
SIKT Pipeline
Used Dataverse API:

/api/search

Extracted metadata from:

JSON response descriptions and titles

Implemented:

Aggressive pagination (up to 2000 results per query)

Exception handling for 429 Too Many Requests (Rate Limiting)

Downloaded:

QDA project files, transcripts, media, and open-document formats.

FSD Pipeline
Used Web Scraping & HTML Parsing

Extracted:

Study titles, dataset IDs

Implemented:

User-Agent header spoofing to bypass strict anti-bot firewalls

Direct targeting of open-access DDI XML metadata files

Stored:

Metadata descriptions directly into the database to feed the classifier

How to Run
1. Run Data Acquisition (Part 1):

Bash
python main.py
2. Run ISIC Rev. 5 Classification (Part 2):

Bash
python classifier.py
Database Structure
Database: 23088045-sq26.db

Column	Description
id	Primary Key
url	Source URL (Unique constraint)
repository	Source repository (sikt or fsd)
filename	Name of the downloaded file
local_dir	Download path for the file
file_hash	SHA-256 hash for integrity
description	Extracted metadata / abstract
isic_division	ISIC Rev. 5 Division (Assigned by Classifier)
tags	Auto-generated keyword tags
Results Summary
Metric	Value
Repositories Targeted	2
Search Queries Used	50+
File Extensions Tracked	80+
Concurrency Level	3 Threads (Throttled for safety)
File Types
QDA Files (Primary Target)
.qdpx, .mqda, .mx24, .nvp, .atlproj, .ppj, etc.

Associated / Primary Files
.pdf, .docx, .txt, .csv, .xlsx, .zip, .mp3, .mp4

Limitations
1. FSD Data Restrictions
FSD strictly protects raw qualitative transcripts (requires academic login).

Workaround: Downloaded open DDI XML metadata files instead, ensuring the classifier still receives rich text data to work with.

2. Server Firewalls & DDoS Protection
High-speed concurrent scraping triggered [Errno 61] Connection refused on SIKT.

Workaround: Implemented thread limits (MAX_THREADS = 3) and "politeness delays" (time.sleep()) to respect server infrastructure.

3. Lack of Raw QDA Files
True QDA software files (like .mx24 or .nvpx) are still relatively rare.
→ Indicates real-world gap:

Researchers often share raw transcripts or PDFs rather than their active coding files.

Technical Challenges
Programming Challenges
SQLite Multithreading Crashes
Problem: Signal 11 (SIGSEGV) crashes occurred when multiple threads attempted to write to the database simultaneously.
Solution: Implemented a strict threading.Lock() in the database manager to force sequential writes.

Bot Detection & Denied Access
Problem: FSD returned 0 results because default Python requests were blocked.
Solution: Spoofed User-Agent headers to mimic a standard Google Chrome browser, successfully bypassing the firewall.

Unstructured Metadata for Classification
Problem: To satisfy Part 2 (Classification), the ISIC classifier needed text, but not all repositories returned clean descriptions.
Solution: Engineered the downloader to safely default to parsing filenames and injected XML data when proper descriptions were missing.

Key Findings
Automated classification is highly dependent on the quality of repository metadata.

Access restrictions remain the highest barrier to acquiring raw qualitative data.

Integrating a backoff/retry strategy is critical when harvesting institutional archives.

Improvements Made
ISIC Rev. 5 Classifier: Built an advanced NLP/Regex-weighted categorization engine.

Project Reconstructor: Script that groups isolated downloaded files back into cohesive dataset folders.

Thread-Safe Architecture: Protected the database from corruption during concurrent networking.

Custom Config: Highly tuned configurations capturing over 80+ file variations (including Mac/PC specific software extensions).

# Project Structure

```text
QDArchive/
│
├── config.py                  # Global settings, file extensions, and queries
├── main.py                    # Acquisition execution script
├── classifier.py              # ISIC Rev. 5 classification script
├── logger.py                  # Centralized logging
│
├── database/
│   └── database.py            # Thread-safe SQLite manager
│
├── downloader/
│   └── downloader.py          # Resilient download engine with backoff logic
│
├── repositories/
│   ├── fsd_client.py          # FSD Web Scraper (Bot bypass)
│   └── sikt_client.py         # SIKT Dataverse API Client
│
├── utils/
│   ├── file_utils.py          # Validation logic
│   ├── hash_utils.py          # SHA-256 generation
│   └── project_reconstructor.py # Re-assembles project directories
│
├── downloads/                 # Local storage for all downloaded data
├── 23088045-sq26.db           # Main SQLite Database
└── README.md
This project successfully demonstrates:

An aggressive but polite automated data acquisition pipeline.

Advanced bypasses for repository rate limits and bot-detection.

Automated taxonomy classification down to the ISIC Rev. 5 Division level.

Transparent and thread-safe database storage.

Despite the inherent limitations of open-access research data, this pipeline provides a sophisticated, scalable foundation for the QDArchive platform.
