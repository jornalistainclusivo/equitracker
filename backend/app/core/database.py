from neo4j import GraphDatabase, AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

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

        try:
            # Using AsyncGraphDatabase for FastAPI async support
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info("Neo4j driver initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            raise e

    async def verify_connectivity(self) -> bool:
        """Verifies connection to the database."""
        if not self.driver:
            logger.warning("Neo4j driver is not initialized.")
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
