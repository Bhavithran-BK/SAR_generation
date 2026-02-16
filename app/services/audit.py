from datetime import datetime
import uuid
import hashlib
from app.models.sql import AuditBlock
from app.db.base import async_session_factory

class AuditService:
    async def log_action(self, action: str, user_id: str, data: dict, previous_hash: str = "0"):
        """
        Log an immutable audit record. where 'data' is what we want to secure.
        """
        data_str = str(data)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        # In a real blockchain-lite implementation, previous_hash would be fetched from the last block.
        # For prototype, we just placeholder it or query the last block.
        
        async with async_session_factory() as session:
            # simple mock of getting last hash
            # stmt = select(AuditBlock).order_by(AuditBlock.timestamp.desc()).limit(1)
            # result = await session.execute(stmt)
            # last_block = result.scalars().first()
            # if last_block:
            #     previous_hash = last_block.data_hash
            
            block = AuditBlock(
                block_id=str(uuid.uuid4()),
                previous_hash=previous_hash,
                timestamp=datetime.utcnow(),
                action=action,
                user_id=user_id,
                data_hash=data_hash
            )
            session.add(block)
            await session.commit()
            
audit_service = AuditService()
