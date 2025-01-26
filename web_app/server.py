from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from openai import OpenAI
import random
import fitz
from munch import Munch
from conversation import initialize_chatbot
from data_pipeline import fetch_research_papers, extract_insight, analyze_paper_support, analyze_overall_sentiment
from dashboard_utilities import createDashboardData, convert_to_jsonable
from haystack.dataclasses import ChatMessage

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global variables for the chatbot
rag_conversation = None
system_message = None
user_message = None

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(filepath)
        print(extracted_text)
        insight : dict = {"title" : filename, 
            "abstract" : extracted_text,
            "keywords" : []
            }
        # Replace with your own logic for insights extraction
        research_paper = Munch(insight)
        industry_insight = extract_insight(research_paper, openai_client)
        industry_insight =  industry_insight.model_dump()
        
        return jsonify({"insight": industry_insight})
    return jsonify({"error": "No file uploaded"}), 400

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using PyMuPDF (fitz).
    :param pdf_path: Path to the PDF file.
    :return: Extracted text as a string.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:  # Iterate through pages
                text += page.get_text()  # Extract text from each page
    except Exception as e:
        text = f"Error extracting text: {str(e)}"
    return text

@app.route('/generate', methods=['POST'])
def generate_from_keywords():
    data = request.json
    keywords : str = data.get('keywords', "")
    keywords = keywords.replace(", ", "+")
    keywords = keywords.replace(" ", "+")
    papers = fetch_research_papers(keywords, 5)
    if papers:
        random_choice = 0
        if len(papers) > 1:
            random_choice = random.randrange(0, len(papers))
        insight = extract_insight(papers[random_choice], openai_client) # research paper to insight
        insight = insight.model_dump()
        print(insight)
        return jsonify({"insight": insight})
    return jsonify({"error": "No papers found"}), 400


@app.route('/research_reengineering', methods=['POST'])
def research_reengineering():
    data = request.json
    claim = data.get('claim', "").strip()
    if not claim:
        return jsonify({"error": "No claim provided"}), 400

    try:
        # Step 1: Generate search parameters
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
        search_params = completion.choices[0].message.content.strip()

        # Step 2: Fetch research papers
        research_papers = fetch_research_papers(search_params, max_results=2)
        if not research_papers:
            return jsonify({"error": "No research papers found"}), 404

        # Step 3: Analyze support/refute for each paper
        table_entries = [
            analyze_paper_support(paper, claim, openai_client).model_dump()
            for paper in research_papers
        ]
        
        sentiment = analyze_overall_sentiment(table_entries, claim, openai_client)
        
        data = {
            "sentiment" : f"{sentiment}",
            "papers": table_entries
        }
        json_data = jsonify(data)
        # Step 4: Return results
        return json_data

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/research_reengineering', methods=['GET'])
def research_reengineering_page():
    return render_template('research_reengineering.html')


@app.route('/generate_dashboard', methods=['POST'])
def generate_dashboard():
    # Replace this example data with actual logic
    # Example: Query a database, calculate trends, etc.
    
    data = request.json
    claim = data.get('claim', "").strip()
    if not claim:
        return jsonify({"error": "No claim provided"}), 400
    
    data = createDashboardData(claim, openai_client)
    
    json_data = convert_to_jsonable(data)
    
    return jsonify(json_data)


@app.route('/initialize_chatbot', methods=['POST'])
def start_chatbot():
    try:
        data = request.json
        claim = data.get('claim', "").strip()
        if not claim:
            return jsonify({"success": False, "error": "No claim provided"}), 400

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
        search_params = completion.choices[0].message.content.strip()

        # Initialize the chatbot with the search parameters
        global rag_conversation, system_message, user_message
        rag_conversation, system_message, user_message = initialize_chatbot(user_subject=search_params, no_papers=20)

        # Respond with success
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        # Parse the request JSON
        data = request.json
        question = data.get('question', "").strip()
        if not question:
            return jsonify({"success": False, "error": "No question provided"}), 400

        # Define system and user messages
        global system_message, user_message, rag_conversation
        messages = [system_message, user_message]

        # Run the conversational RAG pipeline
        res = rag_conversation.run(
            data={
                "query_rephrase_prompt_builder": {"query": question},
                "prompt_builder": {"template": messages, "query": question},
                "memory_joiner": {"values": [ChatMessage.from_user(question)]},
            },
            include_outputs_from=["llm", "query_rephrase_llm"]
        )

        # Extract the chatbot's response
        search_query = res['query_rephrase_llm']['replies'][0]
        assistant_response = res['llm']['replies'][0]

        return jsonify({
            "success": True,
            "search_query": search_query,
            "response": assistant_response.text
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    
if __name__ == '__main__':
    app.run(debug=True)