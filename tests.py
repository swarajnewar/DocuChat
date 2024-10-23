import PyPDF2
import time
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pprint as pprint

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def chunk_text(text, max_chunk_size=50):
    sentences = text.split('.')
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) <= max_chunk_size:
            chunk += sentence + '. '
        else:
            chunks.append(chunk.strip())
            chunk = sentence
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def get_embeddings(text_chunks):
    embeddings = model.encode(text_chunks)
    return embeddings

def index_embeddings(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def get_query_embedding(query):
    return model.encode([query])

def generate_answer(context, query):
    prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
    response = ollama_generate(prompt)
    return response

def retrieve_documents(query_embedding, index, k=5):
    distances, indices = index.search(query_embedding, k)
    return indices

import subprocess

def ollama_generate(prompt, model_name='llama3.2'):
    try:
        command = ['ollama', 'run', model_name]
        result = subprocess.run(
            command,
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,           # Enable text mode (string I/O)
            encoding='utf-8',    # Use UTF-8 encoding
            errors='replace',    # Replace undecodable bytes
            check=True           # Raise exception on non-zero exit
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Ollama: {e.stderr}")
        return None

def main(query):
    text = extract_text_from_pdf("WEF_The_Global_Cooperation_Barometer_2024.pdf")
    text_chunks = chunk_text(text)
    embeddings = get_embeddings(text_chunks)
    index = index_embeddings(embeddings)
    #
    # query = "Can I stack a plus two on top of another plus 2?"
    # query_vector = model.encode([query])
    # k = 5  # Number of nearest neighbors
    # D, I = index.search(query_vector, k)
    #
    # for idx in I[0]:
    #     print(f"Matched Text: {chunks[idx]}")

    query_embedding = get_query_embedding(query)
    indices = retrieve_documents(query_embedding, index)
    # context = " ".join([text_chunks[i] for i in indices])
    answer = generate_answer("", query)

    print(answer)


if __name__ == "__main__":
    query = "Lithium Ion batteries ka price kya hai in general?"
    main(query)