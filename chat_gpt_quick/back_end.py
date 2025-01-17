from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from entities import ResearchPaper, IndustryInsight
from data_pipeline import fetch_research_papers, extract_insight
from openai import OpenAI

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Process file (e.g., extract text using a library like PyPDF2)
        extracted_text = "Mock extracted text from PDF"  # Replace with actual extraction logic
        research_paper = ResearchPaper(title=filename, abstract=extracted_text, authors=[], keywords=[])
        insight = extract_insight(research_paper, openai_client)
        return jsonify({"insight": insight.key_insight})
    return jsonify({"error": "No file uploaded"}), 400

@app.route('/generate', methods=['POST'])
def generate_from_keywords():
    data = request.json
    keywords : str = data.get('keywords', "")
    keywords = keywords.replace(", ", "+")
    keywords = keywords.replace(" ", "+")
    papers = fetch_research_papers(keywords, 1)
    if papers:
        insight = extract_insight(papers[0], openai_client) # research paper to insight
        insight = insight.model_dump()
        print(insight)
        return jsonify({"insight": insight})
    return jsonify({"error": "No papers found"}), 400

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
