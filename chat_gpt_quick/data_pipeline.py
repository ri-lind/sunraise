import os
import sqlite3
from dotenv import load_dotenv
from crossref.restful import Works, Etiquette
from munch import Munch
from openai import OpenAI
from typing import List
from entities import ResearchPaper, IndustryInsight
import feedparser
import urllib, urllib.request

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

# Scrape arxiv.org instead of crossref.
def fetch_research_papers(title_query: str, max_results: int = 10):
    """
    Fetch research papers from arXiv using a title-based search query.
    
    The request will have the following form:
    http://export.arxiv.org/api/query?search_query=ti:"electron thermal conductivity"&sortBy=lastUpdatedDate&sortOrder=ascending
    
    :param title_query: The title search string (e.g., 'electron thermal conductivity')
    :param max_results: The maximum number of results to return (not used in the template below)
    :return: A list of research paper entries
    """
    
    base_url = "http://export.arxiv.org/api/query?"

    # Construct the query parameter to search for papers with the title containing the given phrase.
    # Note: The double quotes need to be included in the query.
    search_query = f'all:{title_query}'
    start = 0                     # retreive the first 5 results
    # Create dictionary for query parameters. The max_results parameter is not shown in the template URL,
    # but you can include it if needed.
     
    
    url = f'{base_url}search_query={search_query}&start={start}&max_results={max_results}'

    
    print("Request URL:", url)  # Optional: print the URL for debugging
    
    # Parse the response using feedparser
    api_response = feedparser.parse(url)
    api_response = Munch(api_response)

    # Process the entries, converting each to a Munch object for easier attribute access
    research_papers = []
    for entry in api_response.entries:
        entry = Munch(entry)
        research_papers.append(entry)
    
    return research_papers

# Convert research paper to industry insight
def extract_insight(research_paper: Munch, client: OpenAI):
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
