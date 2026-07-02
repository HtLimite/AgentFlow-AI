class AgentFlowError(Exception):
    """Base application error."""


class ModelProviderError(AgentFlowError):
    """Raised when a model provider request fails."""


class UnsafeToolInputError(AgentFlowError):
    """Raised when a tool input violates safety restrictions."""
