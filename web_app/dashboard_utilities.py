from openai import OpenAI
import feedparser
from munch import Munch
from data_pipeline import analyze_paper_support
from entities import TableEntryResearchPaper
import time
import random


def createDashboardData(claim, openai_client : OpenAI):
    # 3 years back with 3 papers each.
    # extract the subject from the claim, with a prompt.
    # use the claim to make a request to arxiv with lookback period for year.
    # three papers from each year, might need separate api request
    # get the papers
    # extract the kpis from each of them or average over their number or view count or so
    # return the data in the format of the format for the chart.
    
    search_params_prompt = (
            f"Transform the following user claim into a concise search query for academic research. "
            f"- Use only the most relevant keywords from the claim. "
            f"- Separate the keywords with a '+' to make the query compatible with search engines like arXiv. "
            f"- Remove unnecessary words such as 'the,' 'of,' or 'and.' "
            f"- The resulting query should prioritize precision and relevance, focusing on the core concepts of the claim.\n\n"
            f"Example:\n"
            f"Claim: 'Artificial intelligence helps optimize energy efficiency in data centers.'\n"
            f"artificial+intelligence+energy+efficiency+data+centers\n\n"
            f"Now, process this claim:\n"
            f"Claim: '{claim}'"
        )
    completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Transform user claims into search parameters for academic research."},
                {"role": "user", "content": search_params_prompt},
            ]
        )
    research_papers = return_research_papers(completion)
    
    augment_if_not_three_months(research_papers, claim, openai_client)
    
    return process_research_papers_with_openai(research_papers, claim, openai_client) # returns days and and the average scores.

def process_research_papers_with_openai(research_papers : dict, claim : str, client : OpenAI):
    """
    Processes the research papers dictionary by sending each paper's title and abstract to the OpenAI API.
    
    :param research_papers: Dictionary containing research papers grouped by month
    :param openai_client: OpenAI API client instance
    :return: A dictionary mapping each paper's ID to the OpenAI API's response
    """
    responses = {}
    
    for month, papers in research_papers.items():
        paper_score_list = []
        for paper in papers:
            paper : TableEntryResearchPaper = analyze_paper_support(paper, claim, client)
            paper_score_list.append(paper.support_score)
        
        sum_of_scores = 0
        for score in paper_score_list:
            sum_of_scores = sum_of_scores + score
        if len(paper_score_list) != 0:
            average_score = sum_of_scores / len(paper_score_list)
            responses[month] = average_score
    
    return responses


def get_latest_month_year(url : str)-> int:
    api_response = feedparser.parse(url)
    all_entries = Munch(api_response)
    latest_entry = all_entries.entries[0]
    year = int(latest_entry.updated[:4])
    month = int(latest_entry.published[5:7])
    return (month, year) # return the month of the first entry of this publication.



def return_research_papers(completion):
    search_params = completion.choices[0].message.content.strip()
    base_url = "http://export.arxiv.org/api/query?"

    # Construct the query parameter to search for papers with the title containing the given phrase.
    search_query = f'all:{search_params}'
    start = 0
    research_papers = {}
    
    # take care of current month
    starting_month_url = f'{base_url}search_query={search_query}&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending'
    starting_month, starting_year = get_latest_month_year(starting_month_url)
    research_papers[(starting_month, starting_year)] = []
    api_response = feedparser.parse(starting_month_url)
    api_response = Munch(api_response)
    for entry in api_response.entries:
        research_papers[(starting_month, starting_year)].append(entry)
    # dictionary contains current month
    
    step_size = 50  # Initial batch size
    max_samples = 3  # Number of papers to sample per month
    currentMonth = starting_month - 1 if starting_month > 1 else 12
    currentYear = starting_year if currentMonth != 12 else starting_year-1
    while len(research_papers.keys()) <= 2:  # Targeting at least 4 months of data
        # Adjust batch size after timeout

        # Fetch data from the API
        url = f'{base_url}search_query={search_query}&start={start}&max_results={step_size}&sortBy=submittedDate&sortOrder=descending' 
        api_response = feedparser.parse(url)
        api_response = Munch(api_response)

        # Get all entries in the current batch
        entries = api_response.entries
        if not entries:
            start = start + step_size
            continue
        if int(entries[-1].updated[5:7]) == currentMonth:  # if last element's month is the current iteration's
            # Group papers by month
            for entry in entries[::-1]:
                entry = Munch(entry)
                date_str = entry.updated[:10]  # Extract the 'YYYY-MM-DD' format
                month = int(entry.updated[5:7])  # Extract the month
                year = int(entry.updated[:4])  # Extract the year

                if (month, year) not in research_papers.keys():
                    research_papers[(month, year)] = []

                # Add papers until the max_samples limit is reached
                if len(research_papers[(month, year)]) < max_samples:
                    research_papers[(month, year)].append(entry)
                else:
                    currentMonth = currentMonth - 1 if currentMonth > 1 else 12
                    if currentMonth == 12:
                        currentYear = currentYear -1
                    break
        
        # Update start for the next batch
        if len(research_papers.keys()) <= 4:
            start += step_size

    return research_papers



def augment_if_not_three_months(research_papers: dict, claim: str, openai_client: OpenAI):
    """
    Augments the research_papers dictionary if fewer than 3 months of data are available
    by generating a broader query using OpenAI and analyzing the returned papers.

    :param research_papers: Dictionary containing research papers grouped by month.
    :param claim: The user's claim in natural language.
    :param openai_client: OpenAI client instance.
    """
    if len(research_papers.keys()) < 3:
        # Broader search query prompt
        search_params_prompt = (
            f"Transform the following user claim into a broad and inclusive search query for academic research. "
            f"- Extract only the core concepts from the claim and generalize specific terms into broader categories. "
            f"- Avoid overly specific terms like names of tools, technologies, or datasets. Instead, use general terms "
            f"that encompass a wider range of research. For example, replace 'Copilot' with 'AI tools for coding.' "
            f"- Separate the keywords with a '+' to make the query compatible with search engines like arXiv. "
            f"- Remove unnecessary words such as 'the,' 'of,' or 'and.' "
            f"- The resulting query should prioritize breadth and inclusivity to cover a diverse set of research articles.\n\n"
            f"Example:\n"
            f"Claim: 'Artificial intelligence helps optimize energy efficiency in data centers.'\n"
            f"Query: 'artificial+intelligence+energy+efficiency+optimization+data'\n\n"
            f"Claim: 'Knowing how to use Copilot is beneficial for coding.'\n"
            f"Query: 'ai+tools+coding+benefits+software+development'\n\n"
            f"Claim: 'Python is the best language for data science.'\n"
            f"Query: 'programming+languages+data+science+applications'\n\n"
            f"Make sure to not include the Query: part in the url.\n\n"
            f"Now, process this claim:\n"
            f"Claim: '{claim}'"
        )
        
        # Generate broader search query using OpenAI
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Transform user claims into broad search parameters for academic research."},
                {"role": "user", "content": search_params_prompt},
            ]
        )
        
        # Extract the broader query
        broader_query = completion.choices[0].message.content.strip()

        # Fetch additional research papers using the broader query
        additional_papers = return_research_papers(completion)

        # Analyze each paper's support for the claim and update the dictionary
        for (month, year), papers in additional_papers.items():
            analyzed_papers = []
            for paper in papers:
                analyzed_paper = analyze_paper_support(paper, claim, openai_client)
                analyzed_papers.append(analyzed_paper)
            
            # Add or merge analyzed papers into the research_papers dictionary
            if month not in research_papers:
                research_papers[(month, year)] = analyzed_papers
            else:
                research_papers[(month, year)].extend(analyzed_papers)
