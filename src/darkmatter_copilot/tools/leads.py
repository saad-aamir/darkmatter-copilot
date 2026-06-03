"""MCP tools for managing leads."""

from contextlib import closing

from mcp.server.fastmcp import FastMCP

from darkmatter_copilot.db import get_connection
from darkmatter_copilot.models import LeadCreate, LeadRead, LeadStatus


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def create_lead(lead: LeadCreate) -> LeadRead:
        """Create a new lead and add it to the studio's pipeline.

        Call this tool when the user describes a new prospective client, referral,
        or outbound prospect they want to track. Returns the created lead with
        its assigned id and timestamp.
        """
        with closing(get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO leads (
                        company, contact_name, contact_email, contact_phone,
                        website_url, source, source_detail, existing_client_id,
                        status, business_type, notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        lead.company,
                        lead.contact_name,
                        lead.contact_email,
                        lead.contact_phone,
                        lead.website_url,
                        lead.source,
                        lead.source_detail,
                        lead.existing_client_id,
                        lead.status,
                        lead.business_type,
                        lead.notes,
                    ),
                )
                new_id = cursor.lastrowid
                row = conn.execute("SELECT * FROM leads WHERE id = ?", (new_id,)).fetchone()

        return LeadRead.model_validate(dict(row))

    @mcp.tool()
    def list_leads(status: LeadStatus | None = None) -> list[LeadRead]:
        """List all leads in the database with an optional filter by status.

        Call this tool when the user wants to see all the leads in the database. If the status is provided, only return leads with that status.
        Otherwise, return all leads.
        """

        with closing(get_connection()) as conn:
            if status:
                cursor = conn.execute(
                    "SELECT * FROM leads WHERE status = ? ORDER BY created_at DESC", (status,)
                )
            else:
                cursor = conn.execute("SELECT * FROM leads ORDER BY created_at DESC")

            rows = cursor.fetchall()

            leads = []
            for row in rows:
                lead = LeadRead.model_validate(dict(row))
                leads.append(lead)

            return leads
