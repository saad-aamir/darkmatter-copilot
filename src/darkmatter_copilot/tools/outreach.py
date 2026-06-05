"""MCP tool to draft outreach email."""

from contextlib import closing
from mcp.server.fastmcp import FastMCP
from pathlib import Path

from darkmatter_copilot.db import get_connection
from darkmatter_copilot.models import CaseStudyRead, LeadRead, OutreachContext, WebsiteFindingRead

RESOURCE_DIR = Path(__file__).parent.parent / "resources"


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def draft_outreach_email(lead_id: int, angle: str | None = None) -> OutreachContext:
        """Draft outreach email.

        Call this tool when the user wants to draft an outreach email for a particular lead.
        The user can also send in an optional angle to focus on.
        """

        with closing(get_connection()) as conn:
            cursor = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            lead_row = cursor.fetchone()
            if lead_row is None:
                raise ValueError(f"No lead found with id {lead_id}")
            lead = LeadRead.model_validate(dict(lead_row))

            finding_rows = conn.execute(
                "SELECT * FROM website_findings WHERE lead_id = ? ORDER BY observed_at DESC",
                (lead_id,),
            ).fetchall()
            findings = []
            for row in finding_rows:
                finding = WebsiteFindingRead.model_validate(dict(row))
                findings.append(finding)

            case_studies_rows = conn.execute(
                "SELECT * FROM case_studies ORDER BY created_at DESC"
            ).fetchall()
            case_studies = []
            for row in case_studies_rows:
                row_dict = dict(row)
                if row_dict["tech_stack"]:
                    row_dict["tech_stack"] = row_dict["tech_stack"].split(",")
                else:
                    row_dict["tech_stack"] = []
                case_studies.append(CaseStudyRead.model_validate(row_dict))

        voice_guide = (RESOURCE_DIR / "positioning.md").read_text()
        suggested_structure = (RESOURCE_DIR / "outreach.md").read_text()

        return OutreachContext(
            lead=lead,
            findings=findings,
            case_studies=case_studies,
            voice_guide=voice_guide,
            suggested_structure=suggested_structure,
            angle=angle,
        )
