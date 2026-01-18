"""
Integrations package for external API clients.
"""

from app.integrations.microsoft_graph import graph_client, MicrosoftGraphClient

__all__ = ["graph_client", "MicrosoftGraphClient"]
