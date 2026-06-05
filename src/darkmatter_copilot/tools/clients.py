"""MCP tools for managing clients"""

from contextlib import closing

from mcp.server.fastmcp import FastMCP

from darkmatter_copilot.db import get_connection
from darkmatter_copilot.models import ClientRead


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_clients() -> list[ClientRead]:
        """List all clients.

        Call this tool when the user wants information about all the clients.
        It also returns the number of projects done with the client."""

        with closing(get_connection()) as conn:
            query = """
                SELECT clients.*,
                (SELECT COUNT(*) FROM projects WHERE projects.client_id = clients.id) AS project_count
                FROM clients
                ORDER BY clients.became_client_at DESC
                """

            cursor = conn.execute(query)
            rows = cursor.fetchall()

            clients = []
            for row in rows:
                client = ClientRead.model_validate(dict(row))
                clients.append(client)

            return clients
