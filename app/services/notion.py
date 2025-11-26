import logging
from app.models.data_models import Conversation

logger = logging.getLogger(__name__)


class NotionService:
    
    def __init__(self):
        pass
    
    def save_conversation(self, conversation: Conversation) -> bool:
        logger.warning("Notion integration not implemented")
        return False


