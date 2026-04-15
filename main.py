import os
from concurrent.futures import ThreadPoolExecutor

from config import BASE_DOWNLOAD_DIR, MAX_THREADS, SEARCH_QUERIES
from logger import logger

# Database and Downloader
from database.database import MetadataDatabase
from downloader.downloader import Downloader

# Targeted Repositories ONLY
from repositories.fsd_client import FSDClient
from repositories.sikt_client import SiktClient

# Reconstruction
from utils.project_reconstructor import ProjectReconstructor


def main():

    logger.info("Starting QDArchive Acquisition Pipeline (Target: FSD & SIKT)")

    os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)

    db = MetadataDatabase()
    downloader = Downloader(db)

    # Reconstructor set up with the correct directory string
    reconstructor = ProjectReconstructor(BASE_DOWNLOAD_DIR)

    # Initialize ONLY the assigned repository clients
    fsd = FSDClient()
    sikt = SiktClient()

    tasks = []

    logger.info("Searching targeted repositories...")

    for q in SEARCH_QUERIES:

        logger.info(f"Running query: {q}")

        # FSD Search
        try:
            tasks.extend(fsd.search(q))
        except Exception as e:
            logger.error(f"FSD error for query '{q}': {e}")

        # SIKT Search
        try:
            tasks.extend(sikt.search(q))
        except Exception as e:
            logger.error(f"SIKT error for query '{q}': {e}")

    logger.info(f"Total files discovered across FSD and SIKT: {len(tasks)}")

    if len(tasks) == 0:
        logger.warning("No files discovered. Check your internet connection or API status.")
        return

    logger.info("Starting targeted downloads...")

    # Execute downloads concurrently
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(downloader.download, tasks)

    logger.info("Download phase completed.")

    # Count final success
    try:
        total = db.count()
        logger.info(f"Total files successfully stored in database: {total}")
    except Exception as e:
        logger.error(f"Failed to count database files: {e}")

    logger.info("Reconstructing qualitative research projects...")

    # Bundle files back together
    try:
        reconstructor.reconstruct()
        logger.info("Dataset reconstruction completed.")
    except Exception as e:
        logger.warning(f"Reconstruction failed: {e}")

    logger.info("Pipeline finished successfully. You are now ready for Part 2 Classification!")


if __name__ == "__main__":
    main()
