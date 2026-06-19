# Coding Standards

- All data passed between agents must use Pydantic models defined in core/models.py
- No bare `except:` clauses — always catch specific exceptions
- No print() in production code paths — use observability/logger.py
- All functions that call the Anthropic API must enable prompt caching on system prompts
- Token budget per sub-agent context: max 15,000 tokens, max 10 message turns
- All inter-agent payloads must be JSON-serialisable
