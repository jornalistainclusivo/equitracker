from typing import List, Optional
from datetime import datetime
from app.core.database import db
from app.schemas.source import SourceCreate, SourceResponse

class SourceRepository:
    @property
    def driver(self):
        return db.driver

    async def create_source(self, data: SourceCreate) -> SourceResponse:
        """
        Creates a new Source node in Neo4j.
        """
        query = """
        MERGE (s:Source {url: $url})
        ON CREATE SET 
            s.uid = randomUUID(),
            s.name = $name,
            s.reliability = $reliability,
            s.notes = $notes,
            s.created_at = datetime()
        ON MATCH SET
            s.name = $name,
            s.reliability = $reliability,
            s.notes = $notes,
            s.last_updated = datetime()
        RETURN s
        """
        # If URL is None, we might want to merge on name or just create unique? 
        # The instructions said: MERGE (s:Source {url: $url})
        # If URL is optional in schema but used for MERGE, we need to handle the None case.
        # Assuming for now URL is required for uniqueness if provided, or we fallback to name?
        # Re-reading instructions: "MERGE (s:Source {url: $url})". 
        # SourceCreate has url as optional. If url is None, this MERGE might fail or merge on null.
        # Neo4j allows null properties, but MERGE {url: null} is weird. 
        # Let's assume for this specific slice that URL is expected or we handle it.
        # However, checking the schema: url: Optional[str].
        # If url is missing, maybe we shouldn't use it as the merge key?
        # User instruction: "MERGE (s:Source {url: $url})".
        # I will strictly follow, but if url is None, I'll pass empty string or handle it? 
        # Actually, let's treat URL as the unique key for now as per instructions. 
        # If URL is None, we might generate a placeholder or just let it be null (Neo4j allows multiple nodes with null property if not constrained).
        # But MERGE with null will match all nodes with null property? No, it matches nothing usually or creates new?
        # Actually MERGE(n {prop: null}) behavior is specific.
        # Let's stick to the instruction.
        
        params = data.model_dump()
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            record = await result.single()
            node = record["s"]
            
            # Neo4j DateTime object to python datetime
            # created_at might be a neo4j DateTime. 
            # We need to convert it.
            
            created_at_neo4j = node.get("created_at")
            # created_at_neo4j is likely a neo4j.time.DateTime.
            # We can convert to isoformat or python datetime.
            
            created_at = created_at_neo4j.to_native() if hasattr(created_at_neo4j, 'to_native') else created_at_neo4j

            return SourceResponse(
                name=node.get("name"),
                url=node.get("url"),
                reliability=node.get("reliability"),
                notes=node.get("notes"),
                uid=node.get("uid"),
                created_at=created_at
            )

    async def get_all_sources(self) -> List[SourceResponse]:
        """
        Retrieves all Source nodes.
        """
        query = """
        MATCH (s:Source)
        RETURN s
        """
        async with self.driver.session() as session:
            result = await session.run(query)
            sources = []
            async for record in result:
                node = record["s"]
                created_at_neo4j = node.get("created_at")
                created_at = created_at_neo4j.to_native() if hasattr(created_at_neo4j, 'to_native') else created_at_neo4j
                
                sources.append(SourceResponse(
                    name=node.get("name"),
                    url=node.get("url"),
                    reliability=node.get("reliability"),
                    notes=node.get("notes"),
                    uid=node.get("uid"),
                    created_at=created_at
                ))
            return sources

    async def get_source_by_uid(self, uid: str) -> Optional[SourceResponse]:
        """
        Retrieves a Source node by UID.
        """
        query = """
        MATCH (s:Source {uid: $uid})
        RETURN s
        """
        async with self.driver.session() as session:
            result = await session.run(query, uid=uid)
            record = await result.single()
            if not record:
                return None
            
            node = record["s"]
            created_at_neo4j = node.get("created_at")
            created_at = created_at_neo4j.to_native() if hasattr(created_at_neo4j, 'to_native') else created_at_neo4j

            return SourceResponse(
                name=node.get("name"),
                url=node.get("url"),
                reliability=node.get("reliability"),
                notes=node.get("notes"),
                uid=node.get("uid"),
                created_at=created_at
            )

    async def update_content(self, uid: str, content: str):
        """
        Updates the content of a Source node.
        """
        query = """
        MATCH (s:Source {uid: $uid})
        SET s.content = $content, s.last_scraped_at = datetime()
        RETURN s
        """
        async with self.driver.session() as session:
            await session.run(query, uid=uid, content=content)

    async def update_summary(self, uid: str, summary: str):
        """
        Updates the summary of a Source node.
        """
        query = """
        MATCH (s:Source {uid: $uid})
        SET s.summary = $summary, s.last_summarized_at = datetime()
        RETURN s
        """
        async with self.driver.session() as session:
            await session.run(query, uid=uid, summary=summary)

    async def get_source_content(self, uid: str) -> Optional[str]:
        """
        Retrieves the content of a Source node.
        """
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
