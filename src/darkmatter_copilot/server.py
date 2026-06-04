from mcp.server.fastmcp import FastMCP

from darkmatter_copilot.tools import case_studies, leads, projects

mcp = FastMCP("Dark Matter Co-Pilot")


@mcp.tool()
def hello_studio() -> str:
    """Returns a greeting from the studio.

    Use this tool when the user wants to confirm that mcp server is up and running or when the user
    wants a friendly greeting returned."""

    return "Hello to Dark Matter Studio!"


case_studies.register(mcp)
leads.register(mcp)
projects.register(mcp)

if __name__ == "__main__":
    mcp.run()
