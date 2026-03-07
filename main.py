import os
from concurrent.futures import ThreadPoolExecutor

from config import BASE_DOWNLOAD_DIR, MAX_THREADS, SEARCH_QUERIES
from logger import logger

from database.database import MetadataDatabase
from downloader.downloader import Downloader

# repositories
from repositories.zenodo_client import ZenodoClient
from repositories.dataverse_client import DataverseClient
from repositories.figshare_client import FigshareClient
from repositories.fsd_client import FSDClient
from repositories.sikt_client import SiktClient

# reconstruction
from utils.project_reconstructor import ProjectReconstructor


def main():

    logger.info("Starting QDArchive Acquisition Pipeline")

    os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)

    db = MetadataDatabase()

    downloader = Downloader(db)

    reconstructor = ProjectReconstructor(db)

    # repository clients
    zenodo = ZenodoClient()
    dataverse = DataverseClient()
    figshare = FigshareClient()
    fsd = FSDClient()
    sikt = SiktClient()

    tasks = []

    logger.info("Searching repositories...")

    for q in SEARCH_QUERIES:

        logger.info(f"Running query: {q}")

        try:
            tasks.extend(zenodo.search(q))
        except Exception as e:
            logger.error(f"Zenodo error: {e}")

        try:
            tasks.extend(dataverse.search(q))
        except Exception as e:
            logger.error(f"Dataverse error: {e}")

        try:
            tasks.extend(figshare.search(q))
        except Exception as e:
            logger.error(f"Figshare error: {e}")

        try:
            tasks.extend(fsd.search(q))
        except Exception as e:
            logger.error(f"FSD error: {e}")

        try:
            tasks.extend(sikt.search(q))
        except Exception as e:
            logger.error(f"SIKT error: {e}")

    logger.info(f"Total files discovered: {len(tasks)}")

    if len(tasks) == 0:
        logger.warning("No files discovered. Check repository APIs.")
        return

    logger.info("Starting downloads...")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(downloader.download, tasks)

    logger.info("Download phase completed")

    try:
        total = db.count_files()
        logger.info(f"Total files stored in database: {total}")
    except:
        pass

    logger.info("Reconstructing qualitative research projects...")

    try:
        reconstructor.reconstruct()
        logger.info("Dataset reconstruction completed")
    except Exception as e:
        logger.warning(f"Reconstruction failed: {e}")

    logger.info("Pipeline finished successfully")


if __name__ == "__main__":
    main()