from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.core.database import db
from app.schemas.source import SourceCreate, SourceResponse
import logging

logger = logging.getLogger(__name__)


class SourceRepository:
    @property
    def driver(self):
        return db.driver

    # ─── DRY Helper ────────────────────────────────────────────
    @staticmethod
    def _node_to_response(node) -> SourceResponse:
        """Converts a Neo4j node to a SourceResponse, handling datetime conversion."""
        created_at_neo4j = node.get("created_at")
        if hasattr(created_at_neo4j, 'to_native'):
            created_at = created_at_neo4j.to_native()
        else:
            created_at = created_at_neo4j

        if created_at is None:
            created_at = datetime.now()

        return SourceResponse(
            name=node.get("name") or "Unknown",
            url=node.get("url"),
            inclusion_score=node.get("inclusion_score"),
            reasoning=node.get("reasoning"),
            uid=node.get("uid") or "unknown",
            created_at=created_at,
            suggested_prompts=node.get("suggested_prompts") or []
        )

    # ─── Neo4j Indexes ─────────────────────────────────────────
    async def ensure_indexes(self):
        """Creates indexes and constraints for optimal query performance."""
        queries = [
            "CREATE INDEX source_url_idx IF NOT EXISTS FOR (s:Source) ON (s.url)",
            "CREATE INDEX source_uid_idx IF NOT EXISTS FOR (s:Source) ON (s.uid)",
        ]
        async with self.driver.session() as session:
            for q in queries:
                try:
                    await session.run(q)
                except Exception as e:
                    logger.warning(f"Index creation skipped (may already exist): {e}")

    # ─── CRUD ──────────────────────────────────────────────────
    async def create_source(self, data: SourceCreate) -> SourceResponse:
        """Creates a new Source node in Neo4j."""
        query = """
        MERGE (s:Source {url: $url})
        ON CREATE SET 
            s.uid = randomUUID(),
            s.name = $name,
            s.inclusion_score = $inclusion_score,
            s.reasoning = $reasoning,
            s.created_at = datetime()
        ON MATCH SET
            s.name = $name,
            s.inclusion_score = $inclusion_score,
            s.reasoning = $reasoning,
            s.last_updated = datetime()
        RETURN s
        """
        params = data.model_dump()
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            record = await result.single()
            return self._node_to_response(record["s"])

    async def get_all_sources(self) -> List[SourceResponse]:
        """Retrieves all Source nodes."""
        query = """
        MATCH (s:Source)
        RETURN s
        ORDER BY coalesce(s.last_analyzed_at, s.created_at) DESC
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            sources = []
            async for record in result:
                sources.append(self._node_to_response(record["s"]))
            return sources

    async def get_source_by_uid(self, uid: str) -> Optional[SourceResponse]:
        """Retrieves a Source node by UID."""
        query = """
        MATCH (s:Source {uid: $uid})
        RETURN s
        """
        async with self.driver.session() as session:
            result = await session.run(query, uid=uid)
            record = await result.single()
            if not record:
                return None
            return self._node_to_response(record["s"])

    async def get_source_by_url(self, url: str) -> Optional[SourceResponse]:
        """Retrieves a Source node by URL (uses index)."""
        query = """
        MATCH (s:Source {url: $url})
        RETURN s
        """
        async with self.driver.session() as session:
            result = await session.run(query, url=url)
            record = await result.single()
            if not record:
                return None
            return self._node_to_response(record["s"])

    # ─── Cache ─────────────────────────────────────────────────
    async def get_cached_analysis(self, uid: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Returns cached analysis results if they exist and are fresh.
        Returns None if no cache exists or if the cache is stale.
        """
        query = """
        MATCH (s:Source {uid: $uid})
        WHERE s.inclusion_score IS NOT NULL 
          AND s.last_analyzed_at IS NOT NULL
        RETURN 
            s.inclusion_score AS inclusion_score,
            s.suggested_prompts AS suggested_prompts,
            s.reasoning AS reasoning,
            s.last_analyzed_at AS last_analyzed_at
        """
        async with self.driver.session() as session:
            result = await session.run(query, uid=uid)
            record = await result.single()

            if not record:
                return None

            last_analyzed = record["last_analyzed_at"]
            if hasattr(last_analyzed, 'to_native'):
                last_analyzed = last_analyzed.to_native()

            if last_analyzed is None:
                return None

            # Check freshness
            now = datetime.now(timezone.utc)
            if last_analyzed.tzinfo is None:
                last_analyzed = last_analyzed.replace(tzinfo=timezone.utc)

            age = now - last_analyzed
            if age.total_seconds() > max_age_hours * 3600:
                logger.info(f"Cache stale for {uid} (age: {age}). Will re-analyze.")
                return None

            logger.info(f"Cache HIT for {uid} (age: {age})")
            return {
                "inclusion_score": record["inclusion_score"],
                "suggested_prompts": record["suggested_prompts"] or [],
                "reasoning": record["reasoning"] or "Análise em cache.",
            }

    # ─── Updates ───────────────────────────────────────────────
    async def update_content(self, uid: str, content: str):
        """Updates the content of a Source node."""
        query = """
        MATCH (s:Source {uid: $uid})
        SET s.content = $content, s.last_scraped_at = datetime()
        RETURN s
        """
        async with self.driver.session() as session:
            await session.run(query, uid=uid, content=content)

    async def update_analysis_results(self, uid: str, inclusion_score: int, suggested_prompts: List[str], reasoning: str = ""):
        """Updates the inclusion score, suggested prompts, and reasoning of a Source node."""
        query = """
        MATCH (s:Source {uid: $uid})
        SET s.inclusion_score = $inclusion_score, 
            s.suggested_prompts = $suggested_prompts,
            s.reasoning = $reasoning,
            s.last_analyzed_at = datetime()
        RETURN s
        """
        async with self.driver.session() as session:
            await session.run(
                query,
                uid=uid,
                inclusion_score=inclusion_score,
                suggested_prompts=suggested_prompts,
                reasoning=reasoning,
            )
            
    async def get_source_content(self, uid: str) -> Optional[str]:
        """Retrieves the content of a Source node."""
        query = """
        MATCH (s:Source {uid: $uid})
        RETURN s.content as content
        """
        async with self.driver.session() as session:
            result = await session.run(query, uid=uid)
            record = await result.single()
            if not record:
                return None
            return record["content"]

    # ─── Deletes ───────────────────────────────────────────────
    async def delete_source(self, uid: str) -> bool:
        """Deletes a Source node and its relationships by UID."""
        query = """
        MATCH (s:Source {uid: $uid})
        DETACH DELETE s
        RETURN count(s) as deleted_count
        """
        async with self.driver.session() as session:
            result = await session.run(query, uid=uid)
            record = await result.single()
            return record["deleted_count"] > 0

    async def delete_all_sources(self) -> int:
        """Deletes ALL Source nodes and their relationships."""
        query = """
        MATCH (s:Source)
        DETACH DELETE s
        RETURN count(s) as deleted_count
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            record = await result.single()
            return record["deleted_count"]
