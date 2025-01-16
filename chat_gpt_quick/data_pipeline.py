import os
import sqlite3
from dotenv import load_dotenv
from crossref.restful import Works, Etiquette
from munch import Munch
from openai import OpenAI
from typing import List
from entities import ResearchPaper, IndustryInsight

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database setup
def initialize_database():
    conn = sqlite3.connect("insights.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_papers (
            id INTEGER PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            url TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS industry_insights (
            id INTEGER PRIMARY KEY,
            research_paper_id INTEGER,
            key_insight TEXT,
            use_cases TEXT,
            risks_or_challenges TEXT,
            potential_impact TEXT,
            target_industries TEXT,
            feasibility_score REAL,
            FOREIGN KEY(research_paper_id) REFERENCES research_papers(id)
        )
    """)
    conn.commit()
    return conn

# Fetch research papers from CrossRef API
def fetch_research_papers(keywords: List[str], max_papers: int = 10):
    etiquette = Etiquette('Sunrise Prototype', '1.0', 'N/A', 'r.harizaj@uni-muenster.de')
    works = Works(etiquette=etiquette)
    query = works.query(" ".join(keywords)).filter(has_abstract="true").sort("issued")

    papers = []
    for work in query.sample(max_papers):
        if len(papers) >= max_papers:
            break
        if work.get("title") and work.get("abstract"):
            paper = ResearchPaper(
                title=work["title"][0],
                abstract=work["abstract"],
                url=work.get("URL"),
            )
            papers.append(paper)
    return papers

# Convert research paper to industry insight
def extract_insight(research_paper: ResearchPaper, client: OpenAI):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in extracting valuable insights from research papers. Extract the insight from the following research paper."},
            {"role": "user", "content": research_paper.__str__()},
        ],
        response_format=IndustryInsight,
    )
    return completion.choices[0].message.parsed

# Save data to SQLite database
def save_to_database(conn, research_papers, insights):
    cursor = conn.cursor()

    for paper, insight in zip(research_papers, insights):
        cursor.execute("""
            INSERT INTO research_papers (title, abstract, url)
            VALUES (?, ?, ?)
        """, (paper.title, paper.abstract, paper.url))
        
        research_paper_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO industry_insights (research_paper_id, key_insight, use_cases, risks_or_challenges, potential_impact, target_industries, feasibility_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            research_paper_id,
            insight.key_insight,
            ", ".join(insight.use_cases),
            ", ".join(insight.risks_or_challenges or []),
            insight.potential_impact,
            ", ".join(insight.target_industries),
            insight.feasibility_score
        ))

    conn.commit()

# Main function
def main():
    conn = initialize_database()

    keywords = ["Artificial Intelligence", "Academia", "Industry"]
    research_papers = fetch_research_papers(keywords, max_papers=10)

    insights = []
    for paper in research_papers:
        try:
            insight = extract_insight(paper, openai_client)
            insights.append(insight)
        except Exception as e:
            print(f"Error processing paper {paper.title}: {e}")

    save_to_database(conn, research_papers, insights)
    conn.close()

if __name__ == "__main__":
    main()
