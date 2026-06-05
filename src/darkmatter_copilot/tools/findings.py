"""MCP tools for managing findings of leads."""

from contextlib import closing

from mcp.server.fastmcp import FastMCP

from darkmatter_copilot.db import get_connection
from darkmatter_copilot.models import WebsiteFindingCreate, WebsiteFindingRead


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def record_website_finding(finding: WebsiteFindingCreate) -> WebsiteFindingRead:
        """Record findings of the website for a lead.

        Call this tool when the user wants to record findings for a website of the lead"""

        with closing(get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO website_findings (
                            lead_id,
                            finding,
                            category,
                            severity
                            )
                    VALUES (?, ?, ?, ?)
                    """,
                    (finding.lead_id, finding.finding, finding.category, finding.severity),
                )

                new_id = cursor.lastrowid
                row = conn.execute(
                    "SELECT * FROM website_findings WHERE id = ?", (new_id,)
                ).fetchone()

                finding = WebsiteFindingRead.model_validate(dict(row))
                return finding

    @mcp.tool()
    def list_website_findings(lead_id: int | None = None) -> list[WebsiteFindingRead]:
        """List all findings for a website.

        Call this tool when the user wants to list all findings,
        either for a particular lead or for all leads."""

        with closing(get_connection()) as conn:
            if lead_id is not None:
                cursor = conn.execute(
                    "SELECT * FROM website_findings WHERE lead_id = ? ORDER BY observed_at DESC",
                    (lead_id,),
                )

            else:
                cursor = conn.execute("SELECT * FROM website_findings ORDER BY observed_at DESC")

            rows = cursor.fetchall()

            findings = []
            for row in rows:
                finding = WebsiteFindingRead.model_validate(dict(row))
                findings.append(finding)

            return findings
