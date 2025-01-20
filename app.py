import pymongo
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
from flask import Flask, request, render_template
from sentence_transformers import SentenceTransformer
import json
import os

# MongoDB URI and API Keys
MONGO_URI = "mongodb+srv://userd:12345@cluster0.g8ucp.mongodb.net/testDatabase?retryWrites=true&w=majority"
GEMINI_API_KEY = "AIzaSyB5W7XyaspThPePswHl13jU7CAyCQS6f1Y"  # Replace with your Gemini API key
PINECONE_API_KEY = "pcsk_3Qw7da_5Aj5zuQpZ8ko4vit9eKfGiaoosLsP4KkDyQcaa2DG4ejcbjhMpKgxU1pQ1UgZth"  # Replace with your Pinecone API key
PINECONE_ENV = "us-east-1"  # Replace with your Pinecone environment

print(f"Current Working Directory: {os.getcwd()}")

# Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Pinecone setup
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "project1"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # Dimension for all-MiniLM-L6-v2
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=PINECONE_ENV
        )
    )
pinecone_index = pc.Index(index_name)  # Renommé pour éviter les conflits

# Load the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# MongoDB setup
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["projectAi"]  # Replace with your database name
startup_collection = db["startups"]  # Replace with your collection name

# Function to get examples of startups from MongoDB
def get_startup_examples():
    startups = startup_collection.find().limit(100)
    examples = []
    for startup in startups:
        if 'name' in startup and 'description' in startup and 'secteur' in startup:
            examples.append({
                "name": startup['name'],
                "description": startup['description'],
                "secteur": startup['secteur'],
            })
    return examples

# Function to insert data into Pinecone
def insert_data_into_pinecone(file_path, key):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)[key]
    
    vectors = []
    for item in data:
        data_type = 'step' if 'step' in item else 'law'
        text = f"{item.get('step', '')} {item.get('title', '')} {item.get('description', '')}"
        vector_id = (item.get('step', item.get('law_number', ''))).replace(" ", "_").lower()
        
        embedding = embedding_model.encode(text).tolist()
        vectors.append({
            'id': vector_id,
            'values': embedding,
            'metadata': {
                'type': data_type,
                'title': item.get('title', ''),
                'description': item.get('description', '')
            }
        })

    batch_size = 10
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        pinecone_index.upsert(batch)

# Function to detect query type
def detect_query_type(question):
    # Keywords for each type
    step_keywords = ["step", "create", "startup process", "how to"]
    law_keywords = ["law", "legal", "regulation", "rules"]
    startup_keywords = ["example", "examples", "startup", "startups"]

    if any(keyword in question.lower() for keyword in startup_keywords):
        return "startup"
    elif any(keyword in question.lower() for keyword in step_keywords):
        return "step"
    elif any(keyword in question.lower() for keyword in law_keywords):
        return "law"
    return None

# Function to query Pinecone
def query_pinecone(question):
    question_embedding = embedding_model.encode(question).tolist()
    query_type = detect_query_type(question)  # Determine query type

    if query_type in ["step", "law"]:
        result = pinecone_index.query(
            vector=question_embedding,
            top_k=5,
            include_metadata=True,
            filter={'type': query_type}
        )
        if result and result.get('matches'):
            descriptions = [
                f"- {match['metadata'].get('title', '')}: {match['metadata'].get('description', 'No description available.')}"
                for match in result['matches']
            ]
            return "\n".join(descriptions)  # Use '\n' instead of '<br>'
    return "No matches found."

# Function to query Gemini if needed
def query_with_gemini(question, fallback_context=""):
    """
    Query Gemini if no relevant data is found in MongoDB or Pinecone.
    """
    prompt = f"Answer the following question: {question}\n\n{fallback_context}"
    gemini_response = model.generate_content(prompt)
    return gemini_response.text if gemini_response else "Aucune réponse trouvée."

# Insert steps and laws into Pinecone
insert_data_into_pinecone("visual-ai/steps_to_create_startup_in_morocco.json", "steps_to_create_startup_in_morocco")
insert_data_into_pinecone("visual-ai/laws_in_morocco_about_startups_and_enterprises.json", "laws_in_morocco_about_startups_and_enterprises")

# Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    answer = ""
    if request.method == "POST":
        question = request.form["question"]
        query_type = detect_query_type(question)

        if query_type == "startup":
            examples = get_startup_examples()
            if examples:
                # Format MongoDB results line by line
                examples_text = "\n".join([
                    f"- {ex['name']}: {ex['description']} (Secteur: {ex['secteur']})" for ex in examples
                ])
                answer = examples_text
            else:
                # If no MongoDB results, fallback to Gemini
                answer = query_with_gemini(question, fallback_context="No startups found in the database.")

        elif query_type in ["step", "law"]:
            pinecone_response = query_pinecone(question)
            if pinecone_response != "No matches found.":
                answer = pinecone_response
            else:
                # If no Pinecone results, fallback to Gemini
                answer = query_with_gemini(question, fallback_context="No matching laws or steps found in Pinecone.")

        else:
            # Default to Gemini if no query type is detected
            answer = query_with_gemini(question)

    return render_template("index.html", answer=answer)


@app.route("/ask", methods=["GET", "POST"])
def ask():
    answer = None
    if request.method == "POST":
        question = request.form.get("question", "")
        # Query Pinecone for relevant answer
        answer = query_pinecone(question)
        if not answer or answer == "No matches found.":
            answer = "Désolé, je n'ai pas trouvé de réponse pertinente à votre question."
    
    return render_template("ask.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
