"""MCP tools for managing projects."""

from contextlib import closing

from mcp.server.fastmcp import FastMCP

from darkmatter_copilot.db import get_connection
from darkmatter_copilot.models import ProjectRead, ProjectStatus


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_projects(
        status: ProjectStatus | None = None, client_id: int | None = None
    ) -> list[ProjectRead]:
        """List all projects with client name included.

        Call this tool when the user wants to see all the projects.
        The result will include project details and the name of the client associated with that project."""

        with closing(get_connection()) as conn:
            conditions = []
            params = []

            if status is not None:
                conditions.append("projects.status = ?")
                params.append(status)

            if client_id is not None:
                conditions.append("projects.client_id = ?")
                params.append(client_id)

            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            query = f"""
                SELECT projects.*,
                clients.name as client_name

                FROM projects
                JOIN clients ON projects.client_id = clients.id
                {where_clause}
                ORDER BY projects.created_at DESC
                """

            cursor = conn.execute(query, params)

            rows = cursor.fetchall()

            projects = []
            for row in rows:
                project = ProjectRead.model_validate(dict(row))
                projects.append(project)

            return projects
