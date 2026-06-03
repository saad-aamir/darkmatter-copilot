from contextlib import closing

from mcp.server.fastmcp import FastMCP

from darkmatter_copilot.db import get_connection
from darkmatter_copilot.models import CaseStudyRead


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_case_studies() -> list[CaseStudyRead]:
        """Returns all case studies for Dark Matter Studio with their full narratives.

        Use this tool when the user wants to see past work, find relevant projects
        to reference, or understand what kinds of projects the studio has shipped.
        Returns each case study's problem, approach, result, and tech stack."""
        with closing(get_connection()) as conn:
            cursor = conn.execute("SELECT * FROM case_studies")
            rows = cursor.fetchall()

        result = []
        for row in rows:
            row_dict = dict(row)
            if row_dict["tech_stack"]:
                row_dict["tech_stack"] = row_dict["tech_stack"].split(",")
            else:
                row_dict["tech_stack"] = []

            case_study = CaseStudyRead.model_validate(row_dict)
            result.append(case_study)

        return result
