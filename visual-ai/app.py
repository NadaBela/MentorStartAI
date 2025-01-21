import pymongo
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
from flask import Flask, request, render_template, jsonify
from sentence_transformers import SentenceTransformer
import json
import os
from transformers import SeamlessM4Tv2Model, AutoProcessor
from transformers import AutoProcessor
import torch
import wave
import io
from pydub import AudioSegment


print(f"Current Working Directory: {os.getcwd()}")

# MongoDB URI and Gemini API Key
MONGO_URI = "mongodb+srv://userd:12345@cluster0.g8ucp.mongodb.net/testDatabase?retryWrites=true&w=majority"
GEMINI_API_KEY = "AIzaSyB5W7XyaspThPePswHl13jU7CAyCQS6f1Y"  # Replace with your actual Gemini API key
PINECONE_API_KEY = "pcsk_3Qw7da_5Aj5zuQpZ8ko4vit9eKfGiaoosLsP4KkDyQcaa2DG4ejcbjhMpKgxU1pQ1UgZth"  # Replace with your actual Pinecone API key
PINECONE_ENV = "us-east-1"  

# Configure the Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# MongoDB setup
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["projectAi"]  # Replace with your database name
startup_collection = db["startups"]  # Replace with your collection name (e.g., "startups")

# Pinecone setup
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "project1"  # Replace with your index name
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region=PINECONE_ENV
        )
    )
pinecone_index = pc.Index(index_name)

# Load the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to get examples of startups from MongoDB
def get_startup_examples():
    startups = startup_collection.find()  # Limiting to 200
    examples = []

    for startup in startups:
        example = {
            "name": startup['name'],
            "description": startup['description'],
            "ville": startup['ville'],
            "fonds_levés": startup['fonds_levés'],
            "secteur": startup['secteur'],
            "date_de_creation": startup['date_de_creation']
        }
        examples.append(example)
    
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


# Function to query Pinecone
def query_pinecone(question):
    question_embedding = embedding_model.encode(question).tolist()
    query_type = "step" if "step" in question.lower() or "create" in question.lower() else "law"
    
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
        return "\n".join(descriptions)
    return "No matches found."



# Insert steps and laws into Pinecone
insert_data_into_pinecone("steps_to_create_startup_in_morocco.json", "steps_to_create_startup_in_morocco")
insert_data_into_pinecone("laws_in_morocco_about_startups_and_enterprises.json", "laws_in_morocco_about_startups_and_enterprises")


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    if request.method == "POST":
        question = request.form["question"]
        
        # Check if the question is related to startups or their examples
        if "startups" in question.lower() or "startup" in question.lower():
            examples = get_startup_examples()
            examples_text = "\n".join([f"Name: {ex['name']}, Description: {ex['description']}, ville: {ex['ville']}, levés de fonds: {ex['fonds_levés']}, secteur: {ex['secteur']}\n" for ex in examples])
            prompt = f"Answer the following question using the provided startup examples:\nQuestion: {question}\n\nExamples:\n{examples_text}"
            # Send the prompt to Gemini and get the response
            gemini_response = model.generate_content(prompt)
            answer = gemini_response.text
        elif "law" in question.lower() or "steps" in question.lower():
            # Use Pinecone for laws and steps
            answer = query_pinecone(question)
        else:
            # If the question is not about startups, use general knowledge
            prompt = f"Answer the following question: {question}"
            gemini_response = model.generate_content(prompt)
            answer = gemini_response.text

    return render_template("index.html", answer=answer)

@app.route("/ask", methods=["GET", "POST"])
def ask():
    answer = ""
    if request.method == "POST":
        question = request.form["question"]
        
        # Check if the question is related to startups or their examples
        if "startups" in question.lower() or "startup" in question.lower():
            examples = get_startup_examples()
            examples_text = "\n".join([f"Name: {ex['name']}, Description: {ex['description']}, ville: {ex['ville']}" for ex in examples])
            prompt = f"Answer the following question using the provided startup examples:\nQuestion: {question}\n\nExamples:\n{examples_text}"
            gemini_response = model.generate_content(prompt)
            answer = gemini_response.text
        elif "law" in question.lower() or "steps" in question.lower():
            answer = query_pinecone(question)
        else:
            prompt = f"Answer the following question: {question}"
            gemini_response = model.generate_content(prompt)
            answer = gemini_response.text
        
    return render_template("ask.html", answer=answer)
chat_history = []

@app.route("/chat", methods=["POST"])
def chat():
    processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
    model1 = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
    data = request.get_json()
    question1 = data.get("user_input", "")
    text_inputs = processor(text = question1 , src_lang="ary", return_tensors="pt")

    # generate translation
    output_tokens = model1.generate(**text_inputs, tgt_lang="eng", generate_speech=False)
    question = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
    
    
    if "startups" in question.lower() or "startup" in question.lower():
        examples = get_startup_examples()
        examples_text = "\n".join([f"Name: {ex['name']}, Description: {ex['description']}, ville: {ex['ville']}" for ex in examples])
        prompt = f"Answer the following question using the provided startup examples:\nQuestion: {question}\n\nExamples:\n{examples_text}"
        gemini_response = model.generate_content(prompt)
        answer = gemini_response.text
    elif "law" in question.lower() or "steps" in question.lower():
        answer = query_pinecone(question)
    else:
        prompt = f"Answer the following question: {question}"
        gemini_response = model.generate_content(prompt)
        answer = gemini_response.text


  
    # Process the user's input and generate a response
    #processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
    #model2 = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")
    #text=answer
    # process input
    #text_inputs = processor(text = text , src_lang="eng", return_tensors="pt")

    # generate translation
    #output_tokens = model2.generate(**text_inputs, tgt_lang="ary", generate_speech=False)
    #translated_text_from_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
    #print(f"Translation from text: {translated_text_from_text}")
    lines = [line.strip() for line in answer.split('.') if line.strip()]
    final_translations = []

    # Initialize the translation processor and model


    for line in lines:
        # Prepare input for translation
        text_inputs = processor(text=line, src_lang="eng", return_tensors="pt")

        # Generate translation
        output_tokens = model1.generate(**text_inputs, tgt_lang="ary", generate_speech=False)
        translated_line = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
        final_translations.append(translated_line)

    # Print and return translated lines
    print("Translated Response:")
    for idx, translated_line in enumerate(final_translations, 1):
        print(f"{idx}: {translated_line}")
    final_result = ". ".join(final_translations) + "."
    
  
    chat_history.append({"sender": "user", "text": question})
    chat_history.append({"sender": "bot", "text": final_result})
    
    return jsonify({"answer": final_result})

if __name__ == "__main__":
    app.run(debug=True)
