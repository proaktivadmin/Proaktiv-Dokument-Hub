"""
Integrations package for external API clients.
"""

from app.integrations.microsoft_graph import MicrosoftGraphClient, graph_client

__all__ = ["graph_client", "MicrosoftGraphClient"]
