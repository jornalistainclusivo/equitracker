import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase, AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

# Path Resolution
ROOT_DIR = Path(__file__).resolve().parents[3]
# load_dotenv(ROOT_DIR / ".env")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"🔍 Project Root detected at: {ROOT_DIR}")

# Load Environment
load_dotenv(ROOT_DIR / ".env")

class Neo4jConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
            cls._instance.driver = None
        return cls._instance

    def connect(self):
        """Initializes the Neo4j driver connection."""
        if self.driver:
            return

        uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")

        if password is None:
            logger.fatal("NEO4J_PASSWORD is not set in environment variables.")
            raise Exception("NEO4J_PASSWORD is not set.")

        try:
            # Using AsyncGraphDatabase for FastAPI async support
            self.driver = AsyncGraphDatabase.driver(
                uri,
                auth=(user, password)
            )
            logger.info(f"Neo4j driver initialized with URI: {uri}")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            raise e

    async def verify_connectivity(self) -> bool:
        """Verifies connection to the database."""
        if not self.driver:
            # Try to connect if not connected
            try:
                self.connect()
            except Exception:
                logger.warning("Neo4j driver is not initialized and connection attempt failed.")
                return False
            
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 AS result")
                record = await result.single()
                if record and record["result"] == 1:
                    logger.info("Neo4j connectivity verified.")
                    return True
        except ServiceUnavailable:
            logger.error("Neo4j service unavailable.")
            return False
        except AuthError:
            logger.error("Neo4j authentication failed.")
            return False
        except Exception as e:
            logger.error(f"Neo4j connection verification failed: {e}")
            return False
        return False

    async def close(self):
        """Closes the driver connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None
            logger.info("Neo4j driver closed.")

db = Neo4jConnection()
