import json
import re
import threading
from pathlib import Path

import anthropic

from config.settings import config
from core.context_manager import ContextManager
from core.models import AdvisoryResponse, Allocation, UserProfile
from core.rules_engine import RulesEngine
from observability.logger import get_logger
from observability.metrics import ACTIVE_SESSIONS, REQUEST_COUNT, REQUEST_LATENCY, TOKEN_USAGE
from rag.retriever import RAGRetriever

logger = get_logger(__name__)

DISCLAIMER = "⚠️ This is an educational demo only. Not real financial advice."

AGENTS_DIR = Path(__file__).parent.parent / ".claude" / "agents"


def _load_agent_prompt(agent_name: str) -> str:
    """Load system prompt from .claude/agents/<name>.md, stripping YAML frontmatter."""
    path = AGENTS_DIR / f"{agent_name}.md"
    text = path.read_text()
    # Strip --- frontmatter block if present
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:].lstrip("\n")
    return text


class InvestmentOrchestrator:
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self._rules_engine = RulesEngine(config.rules_file)
        self._rag = RAGRetriever()
        # Each agent gets its own isolated context
        self._ctx_frontend = ContextManager()
        self._ctx_backend = ContextManager()
        self._ctx_triage = ContextManager()
        # Cache system prompts (loaded once)
        self._prompt_frontend = _load_agent_prompt("frontend-agent")
        self._prompt_backend = _load_agent_prompt("backend-agent")
        self._prompt_triage = _load_agent_prompt("triage-agent")

    def process_advisory_request(self, raw_form_data: dict) -> AdvisoryResponse:
        with REQUEST_LATENCY.time():
            ACTIVE_SESSIONS.inc()
            try:
                return self._run(raw_form_data)
            finally:
                ACTIVE_SESSIONS.dec()

    def _run(self, raw_form_data: dict) -> AdvisoryResponse:
        # Step 1: frontend-agent validates input
        profile = self._validate_input(raw_form_data)
        logger.info("Input validated", extra={"profile": profile.model_dump()})

        REQUEST_COUNT.labels(risk_level=profile.risk, goal=profile.goal).inc()

        # Step 2: rules engine computes allocation (pure Python, no LLM)
        allocation = self._rules_engine.compute_allocation(profile)
        logger.info("Allocation computed", extra={"allocation": allocation.model_dump()})

        # Step 3: RAG retrieves relevant knowledge (pure Python, no LLM)
        rag_query = f"risk={profile.risk} goal={profile.goal} age={profile.age} investment categories"
        rag_context = self._rag.retrieve(rag_query)
        logger.info("RAG retrieved", extra={"passages": len(rag_context)})

        # Step 4: backend-agent generates explanation
        explanation = self._generate_explanation(profile, allocation, rag_context)
        logger.info("Explanation generated")

        response = AdvisoryResponse(
            profile=profile,
            allocation=allocation,
            explanation=explanation,
            disclaimer=DISCLAIMER,
            chart_data=allocation.model_dump(),
        )

        # Step 6: triage-agent runs asynchronously if enabled
        if config.enable_triage:
            threading.Thread(
                target=self._run_triage,
                args=(raw_form_data, allocation, explanation),
                daemon=True,
            ).start()

        return response

    def _validate_input(self, raw_form_data: dict) -> UserProfile:
        """Call frontend-agent to validate raw form data and return a UserProfile."""
        user_msg = json.dumps({"task": "validate", "data": raw_form_data})
        self._ctx_frontend.add_message("user", user_msg)

        result = self._call_agent(
            system_prompt=self._prompt_frontend,
            messages=self._ctx_frontend.get_trimmed_history(),
            model=config.subagent_model,
            agent_name="frontend-agent",
        )
        self._ctx_frontend.add_message("assistant", result)

        parsed = self._parse_json(result)
        if not parsed.get("valid"):
            errors = parsed.get("errors", ["Unknown validation error"])
            raise ValueError(f"Input validation failed: {errors}")

        p = parsed["profile"]
        return UserProfile(
            age=p["age"],
            monthly_income=p["monthly_income"],
            monthly_savings=p["monthly_savings"],
            risk=p["risk"],
            goal=p["goal"],
        )

    def _generate_explanation(
        self, profile: UserProfile, allocation: Allocation, rag_context: list[str]
    ) -> str:
        """Call backend-agent to generate a plain-language explanation."""
        user_msg = json.dumps({
            "user_profile": profile.model_dump(),
            "allocation": allocation.model_dump(),
            "rag_context": rag_context,
        })
        self._ctx_backend.add_message("user", user_msg)

        result = self._call_agent(
            system_prompt=self._prompt_backend,
            messages=self._ctx_backend.get_trimmed_history(),
            model=config.subagent_model,
            agent_name="backend-agent",
        )
        self._ctx_backend.add_message("assistant", result)

        parsed = self._parse_json(result)
        return parsed.get("explanation", result)

    def _run_triage(self, raw_input: dict, allocation: Allocation, explanation: str) -> None:
        """Run triage-agent asynchronously and write report to reports/."""
        import datetime
        from pathlib import Path

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_data = {
            "user_input": raw_input,
            "allocation": allocation.model_dump(),
            "explanation": explanation,
            "timestamp": timestamp,
        }
        self._ctx_triage.add_message("user", json.dumps(session_data))

        try:
            report = self._call_agent(
                system_prompt=self._prompt_triage,
                messages=self._ctx_triage.get_trimmed_history(),
                model=config.triage_model,
                agent_name="triage-agent",
            )
            self._ctx_triage.add_message("assistant", report)

            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            report_path = reports_dir / f"triage_{timestamp}.md"
            report_path.write_text(report)
            logger.info("Triage report written", extra={"path": str(report_path)})
        except Exception as e:
            logger.error("Triage failed", extra={"error": str(e)})

    def _call_agent(
        self,
        system_prompt: str,
        messages: list[dict],
        model: str,
        agent_name: str,
    ) -> str:
        """Call the Anthropic API with prompt caching on the system prompt."""
        request_params: dict = {
            "model": model,
            "max_tokens": 1024,
            "system": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            "messages": messages,
        }

        response = self._client.messages.create(**request_params)

        # Track token usage
        usage = response.usage
        TOKEN_USAGE.labels(agent=agent_name, direction="input").inc(usage.input_tokens)
        TOKEN_USAGE.labels(agent=agent_name, direction="output").inc(usage.output_tokens)

        # Handle tool_use blocks: execute locally and recurse with tool_result
        content = response.content
        tool_use_blocks = [b for b in content if b.type == "tool_use"]
        if tool_use_blocks:
            tool_results = []
            for block in tool_use_blocks:
                result = self._execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })
            # Feed results back
            new_messages = messages + [
                {"role": "assistant", "content": content},
                {"role": "user", "content": tool_results},
            ]
            return self._call_agent(system_prompt, new_messages, model, agent_name)

        return response.content[0].text

    def _execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a tool call locally and return the result."""
        if tool_name == "compute_allocation":
            profile = UserProfile(**tool_input)
            allocation = self._rules_engine.compute_allocation(profile)
            return allocation.model_dump()
        if tool_name == "retrieve_knowledge":
            query = tool_input.get("query", "")
            docs = self._rag.retrieve(query)
            return {"passages": docs}
        raise ValueError(f"Unknown tool: {tool_name}")

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract JSON from agent response, tolerating markdown code blocks."""
        # Strip markdown fences if present
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            text = match.group(1)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find the first {...} block
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {}
