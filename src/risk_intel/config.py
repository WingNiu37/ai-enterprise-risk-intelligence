from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DATABASE_DIR = ROOT / "database"

RISK_CATEGORIES = (
    "Market Risk",
    "Credit Risk",
    "Operational Risk",
    "Technology Risk",
    "Emerging Risk",
)

SECTORS = (
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Health Care",
    "Industrials",
    "Information Technology",
    "Materials",
    "Real Estate",
    "Utilities",
    "Government and Public Sector",
    "Cross-sector",
)

RSS_SOURCES = {
    "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "SEC": "https://www.sec.gov/news/pressreleases.rss",
    "OCC": "https://occ.treas.gov/rss/occ_news.xml",
    "NIST Cybersecurity": "https://www.nist.gov/news-events/cybersecurity/rss.xml",
}
