from core.models import UserProfile
from core.rules_engine import RulesEngine
from config.settings import config
from rag.retriever import RAGRetriever
from observability.logger import get_logger

logger = get_logger(__name__)

# Singletons — created once on import
_rules_engine = RulesEngine(config.rules_file)
_rag = RAGRetriever()


def handle_get_recommendation(body: dict) -> dict:
    try:
        profile = UserProfile(
            age=body["age"],
            monthly_income=body["monthly_income"],
            monthly_savings=body["monthly_savings"],
            risk=body["risk"],
            goal=body["goal"],
        )
        allocation = _rules_engine.compute_allocation(profile)
        logger.info("MCP get_recommendation", extra={"risk": profile.risk, "goal": profile.goal})
        return {"status": "ok", "allocation": allocation.model_dump()}
    except (KeyError, ValueError) as e:
        logger.error("MCP get_recommendation error", extra={"error": str(e)})
        return {"status": "error", "message": str(e)}


def handle_get_knowledge(body: dict) -> dict:
    try:
        query = body["query"]
        passages = _rag.retrieve(query)
        logger.info("MCP get_knowledge", extra={"query": query, "results": len(passages)})
        return {"status": "ok", "passages": passages}
    except KeyError as e:
        return {"status": "error", "message": f"Missing field: {e}"}


def handle_health_check() -> dict:
    return {"status": "ok", "service": "investment-advisor-poc"}
