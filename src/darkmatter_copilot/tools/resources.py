"""MCP resources exposing Dark Matter Studio's pricing, positioning and process docs"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

RESOURCE_DIR = Path(__file__).parent.parent / "resources"


def register(mcp: FastMCP) -> None:
    """Register Dark Matter Studio's reference documents as MCP resources."""

    @mcp.resource("studio://pricing")
    def get_pricing() -> str:
        """Dark Matter Studio's pricing guide: project ranges, scope drivers,
        add-ons. Use this when generating proposals, quoting prices, or
        explaining how the studio prices work.
        """

        return (RESOURCE_DIR / "pricing.md").read_text()

    @mcp.resource("studio://positioning")
    def get_positioning() -> str:
        """Dark Matter Studio's positioning and voice guide: target clients,
        differentiators, and tone of voice. Use this when writing in the
        studio's voice. Proposals, outreach emails, marketing copy.
        """

        return (RESOURCE_DIR / "positioning.md").read_text()

    @mcp.resource("studio://process")
    def get_process() -> str:
        """Dark Matter Studio's delivery process: stages, timeline,
        communication norms, and scoping questions. Use this when describing
        how the studio works or asking discovery questions.
        """
        return (RESOURCE_DIR / "process.md").read_text()
