"""Seed the database with real Dark Matter Studio data.

⚠️  WARNING: This script wipes existing data before inserting.
    Safe to run while the database only contains seed data.
    Once real leads/proposals exist, do not run without backing up.
"""

from contextlib import closing

from darkmatter_copilot.db import get_connection, init_db


CLIENTS = [
    {
        "name": "Sussex Light Photography",
        "contact_name": "Ahsan Yunus",
        "contact_email": "info@sussexlightphotography.com",
        "contact_phone": "+44 7413 565121",
        "notes": "Family project (sister's business via brother-in-law Ahsan).",
    },
    {
        "name": "The Crib Murree",
        "contact_name": "Ahsan Yunus",
        "contact_email": "thecribmurree@gmail.com",
        "contact_phone": "+92 306 544 0665",
        "notes": "Family project (brother-in-law's referred booking site for a Murree property).",
    },
    {
        "name": "FMY Chartered Accountants",
        "contact_name": "Faraz Yunus",
        "contact_email": "farazyunus@gmail.com",
        "contact_phone": None,
        "notes": "Family project (brother-in-law's accountancy firm in London).",
    },
]


# Note: client_id is filled in after clients are inserted (we need their auto-generated IDs).
PROJECTS = [
    {
        "client_name": "Sussex Light Photography",   # used to look up client_id after insert
        "name": "Sussex Light Photography — portfolio site",
        "project_type": "portfolio",
        "scope": (
            "Single-page portfolio site to establish online presence: scrollable "
            "gallery, testimonials, pricing packages, about, and contact section."
        ),
        "price": 0,                                   # free of cost (family rate)
        "paid_at": None,
        "started_at": "2026-03-01",
        "deadline": None,
        "completed_at": "2026-04-30",
        "status": "completed",
        "deployment_url": "https://www.sussexlightphotography.com/",
        "notes": "Family rate — free of cost. Not market-rate pricing.",
    },
    {
        "client_name": "The Crib Murree",
        "name": "The Crib Murree — direct booking site",
        "project_type": "landing_page",
        "scope": (
            "Single-page Next.js site for a boutique hospitality business with two "
            "bookable apartments. Sections for stays, comforts, guest reviews, "
            "rates, and a direct inquiry form (no third-party platform fees)."
        ),
        "price": 50000,                               # PKR
        "paid_at": "2026-05-31",
        "started_at": "2026-05-01",
        "deadline": None,
        "completed_at": "2026-05-31",
        "status": "completed",
        "deployment_url": "https://www.thecribmurree.com/",
        "notes": "Family rate — PKR 50,000. Not market-rate pricing for a project of this scope.",
    },
    {
        "client_name": "FMY Chartered Accountants",
        "name": "FMY Chartered Accountants — corporate website",
        "project_type": "corporate_site",
        "scope": (
            "Multi-page corporate website for a London-based chartered accountancy. "
            "Architecture across 9 service categories, Calendly consultation booking, "
            "chatbot widget for visitor queries, live market data ticker, newsletter "
            "subscription, and content strategy reflecting partner-led positioning."
        ),
        "price": 400,                                 # GBP
        "paid_at": "2026-05-31",
        "started_at": "2026-04-01",
        "deadline": None,
        "completed_at": "2026-05-31",
        "status": "completed",
        "deployment_url": "https://www.fmyaccountants.co.uk/",
        "notes": "Family rate — £400. Real commercial price for this scope would be £3,000-£8,000.",
    },
]


CASE_STUDIES = [
    {
        "project_name": "Sussex Light Photography — portfolio site",
        "problem": (
            "A working photographer with no online presence needed a credible "
            "portfolio site to showcase her work to prospective clients."
        ),
        "approach": (
            "Built a single-page Next.js + Tailwind site with a minimalist aesthetic "
            "matching her brand colors. Included a scrollable gallery, testimonials, "
            "an about section, contact, and a pricing page covering her packages."
        ),
        "result": (
            "Delivered a portfolio site she actively uses to share with prospective "
            "clients. Site has been live since April 2026."
        ),
        "tech_stack": "Next.js,Tailwind CSS,Vercel",
        "is_published": 1,                            # shown on darkmatterstudio.org
        "published_at": "2026-04-30",
    },
    {
        "project_name": "The Crib Murree — direct booking site",
        "problem": (
            "A boutique hospitality property in Murree wanted a direct booking "
            "channel to bypass third-party platform fees and present the property's "
            "atmosphere on their own terms."
        ),
        "approach": (
            "Built a Next.js + Tailwind single-page site with rich photo galleries "
            "for each apartment, a long-form narrative structure (chapters), guest "
            "testimonials, transparent per-night rates, and a direct inquiry form "
            "with response-time commitment."
        ),
        "result": (
            "Shipped a complete direct-booking site that the property now uses as "
            "its primary booking channel, avoiding platform commission fees."
        ),
        "tech_stack": "Next.js,Tailwind CSS,Vercel",
        "is_published": 0,
        "published_at": None,
    },
    {
        "project_name": "FMY Chartered Accountants — corporate website",
        "problem": (
            "A London-based chartered accountancy firm wanted to replace an outdated "
            "website with a modern, partner-led marketing presence that reflected "
            "their Big-4-trained expertise and fixed-fee positioning."
        ),
        "approach": (
            "Built a multi-page Next.js + TypeScript + Tailwind site from scratch. "
            "Designed the information architecture across 9 service categories with "
            "sub-pages, integrated Calendly for consultation bookings, built a "
            "chatbot widget for visitor questions, and added a live market data "
            "ticker. Used Claude Code as a pair programmer to move quickly through "
            "implementation while owning architecture, integration choices, and "
            "content strategy."
        ),
        "result": (
            "Delivered a complete corporate website now in production as FMY's "
            "primary marketing presence."
        ),
        "tech_stack": "Next.js,TypeScript,Tailwind CSS,Vercel,Calendly",
        "is_published": 0,
        "published_at": None,
    },
]


def wipe_database(conn) -> None:
    """Delete all data from all tables. Order respects foreign key dependencies."""
    # Delete in reverse-dependency order:
    # case_studies depends on projects; proposals depends on leads; projects depends on clients
    conn.execute("DELETE FROM case_studies")
    conn.execute("DELETE FROM proposals")
    conn.execute("DELETE FROM projects")
    conn.execute("DELETE FROM leads")
    conn.execute("DELETE FROM clients")
    
    # Reset auto-increment counters so new rows start at id=1 again.
    # sqlite_sequence is SQLite's internal table tracking AUTOINCREMENT state.
    conn.execute("DELETE FROM sqlite_sequence")


def seed() -> None:
    """Wipe and re-seed the database with real studio data."""
    init_db()  # Ensure tables exist
    
    with closing(get_connection()) as conn:
        with conn:  # Transaction: commits on success, rolls back on exception
            wipe_database(conn)
            
            # Insert clients and track their new IDs by name (for FK lookups below)
            client_ids = {}
            for client in CLIENTS:
                cursor = conn.execute(
                    """
                    INSERT INTO clients (name, contact_name, contact_email, contact_phone, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        client["name"],
                        client["contact_name"],
                        client["contact_email"],
                        client["contact_phone"],
                        client["notes"],
                    ),
                )
                client_ids[client["name"]] = cursor.lastrowid
            
            # Insert projects, looking up client_id by name
            project_ids = {}
            for project in PROJECTS:
                cursor = conn.execute(
                    """
                    INSERT INTO projects (
                        client_id, name, project_type, scope, price, paid_at,
                        started_at, deadline, completed_at, status, deployment_url, notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        client_ids[project["client_name"]],
                        project["name"],
                        project["project_type"],
                        project["scope"],
                        project["price"],
                        project["paid_at"],
                        project["started_at"],
                        project["deadline"],
                        project["completed_at"],
                        project["status"],
                        project["deployment_url"],
                        project["notes"],
                    ),
                )
                project_ids[project["name"]] = cursor.lastrowid
            
            # Insert case studies, looking up project_id by name
            for case_study in CASE_STUDIES:
                conn.execute(
                    """
                    INSERT INTO case_studies (
                        project_id, problem, approach, result, tech_stack,
                        is_published, published_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_ids[case_study["project_name"]],
                        case_study["problem"],
                        case_study["approach"],
                        case_study["result"],
                        case_study["tech_stack"],
                        case_study["is_published"],
                        case_study["published_at"],
                    ),
                )
    
    print("Database seeded successfully:")
    print(f"  - {len(CLIENTS)} clients")
    print(f"  - {len(PROJECTS)} projects")
    print(f"  - {len(CASE_STUDIES)} case studies")


if __name__ == "__main__":
    seed()