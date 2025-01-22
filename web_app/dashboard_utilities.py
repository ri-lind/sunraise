from openai import OpenAI
import feedparser
from munch import Munch
from data_pipeline import analyze_paper_support
from entities import TableEntryResearchPaper
import time
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


def get_latest_month(url : str)-> int:
    api_response = feedparser.parse(url)
    all_entries = Munch(api_response)
    latest_entry = all_entries.entries[0]
    return int(latest_entry.published[5:7]) # return the month of the first entry of this publication.


def return_research_papers(completion):
    search_params = completion.choices[0].message.content.strip()
    
    
    base_url = "http://export.arxiv.org/api/query?"

    # Construct the query parameter to search for papers with the title containing the given phrase.
    # Note: The double quotes need to be included in the query.
    search_query = f'all:{search_params}'
    start = 0                     # retreive the first 5 results
    # Create dictionary for query parameters. The max_results parameter is not shown in the template URL,
    # but you can include it if needed.
    research_papers = {}    
    current_month = get_latest_month(f'{base_url}search_query={search_query}&start={start}&max_results={10}&sortBy=submittedDate&sortOrder=descending') # initialize first month without looping logic
    month_counter = 0
    batches = 1000
    
    start_time = time.time()
    while len(research_papers.keys()) <= 4: # this changes the number of months received back on the screen
        if int(time.time() - start_time)> 20: # break if more than 20 seconds.
            break
        papers_of_current_month = research_papers.get(current_month, [])
        url = f'{base_url}search_query={search_query}&start={start}&max_results={batches}&sortBy=submittedDate&sortOrder=descending'
        api_response = feedparser.parse(url)
        api_response = Munch(api_response)
        
        for entry in api_response.entries:
            entry = Munch(entry)
            
            month = int(entry.updated[5:7]) # actually day
            
            if month == current_month and len(papers_of_current_month)< 3: # add a paper to the three of current month
                papers_of_current_month.append(entry)
                
                continue
            elif len(papers_of_current_month) == 3:
                month_counter = month_counter + 1
                research_papers[current_month] = papers_of_current_month.copy()
                if current_month ==1:
                    current_month = 12
                else:
                    current_month = current_month - 1
                papers_of_current_month = research_papers.get(current_month, [])
                continue
            elif month != current_month:
                # either end without next month, go to next batch of 100
                # or paper list could not be completed here.
                if len(papers_of_current_month) < 3:
                    research_papers[current_month] = papers_of_current_month.copy()
                    start = start + batches
                    print(start)
                    break
                
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
        for month, papers in additional_papers.items():
            analyzed_papers = []
            for paper in papers:
                analyzed_paper = analyze_paper_support(paper, claim, openai_client)
                analyzed_papers.append(analyzed_paper)
            
            # Add or merge analyzed papers into the research_papers dictionary
            if month not in research_papers:
                research_papers[month] = analyzed_papers
            else:
                research_papers[month].extend(analyzed_papers)
