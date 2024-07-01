from flask import Flask, request, jsonify, send_file
from transformers import T5Tokenizer, T5ForConditionalGeneration, BertTokenizer, BertForQuestionAnswering, pipeline
from sentence_transformers import SentenceTransformer, util
import torch
from PyPDF2 import PdfReader
import docx
import os
from glob import glob
from fpdf import FPDF

app = Flask(__name__)

# Model loading
checkpoint = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(checkpoint)
base_model = T5ForConditionalGeneration.from_pretrained(checkpoint)
qa_model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
qa_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# File loader and preprocessing
def read_pdf(file_path):
    reader = PdfReader(file_path)
    texts = [page.extract_text() for page in reader.pages]
    return "\n".join(texts)

def read_docx(file_path):
    doc = docx.Document(file_path)
    texts = [para.text for para in doc.paragraphs]
    return "\n".join(texts)

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def file_preprocessing(folder_path):
    file_contents = []
    
    for file_path in glob(os.path.join(folder_path, '*')):
        ext = file_path.split('.')[-1].lower()
        if ext == 'pdf':
            text = read_pdf(file_path)
        elif ext == 'docx':
            text = read_docx(file_path)
        elif ext == 'txt':
            text = read_txt(file_path)
        else:
            continue
        
        file_contents.append(text)
    
    return file_contents

def split_text(text, max_length=512):
    words = text.split()
    chunks = [' '.join(words[i:i+max_length]) for i in range(0, len(words), max_length)]
    return chunks

def llm_pipeline(input_text):
    pipe_sum = pipeline(
        'summarization',
        model=base_model,
        tokenizer=tokenizer,
        framework='pt',
        device=0 if torch.cuda.is_available() else -1  # Use GPU if available
    )
    result = pipe_sum(input_text)
    summary = result[0]['summary_text']
    return summary

def summarize_files(folder_path):
    file_contents = file_preprocessing(folder_path)
    
    # Combine all texts into a single string
    combined_text = " ".join(file_contents)
    
    # Split the combined text into chunks
    chunks = split_text(combined_text)
    
    # Summarize each chunk and combine the summaries
    combined_summary = " ".join([llm_pipeline(chunk) for chunk in chunks])

    # print(combined_summary)

    # final_summary = llm_pipeline(combined_summary)
    
    return combined_summary

def save_summary_to_pdf(summary, output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Handle UTF-8 encoding
    try:
        pdf.multi_cell(0, 10, summary.encode('latin-1', 'replace').decode('latin-1'))
    except UnicodeEncodeError:
        pdf.multi_cell(0, 10, summary.encode('utf-8').decode('utf-8'))
    
    output_pdf_path = os.path.join(output_path, "summary.pdf")
    pdf.output(output_pdf_path)
    
    return output_pdf_path

def query_embeddings(embeddings, query_embedding):
    cos_scores = util.pytorch_cos_sim(query_embedding, embeddings)[0]
    top_idx = torch.argmax(cos_scores).item()
    return top_idx, cos_scores[top_idx].item()

def answer_question(qa_model, qa_tokenizer, context, question):
    encoding = qa_tokenizer.encode_plus(question, context, return_tensors="pt")
    input_ids = encoding["input_ids"].tolist()[0]
    outputs = qa_model(**encoding)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits

    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1

    answer = qa_tokenizer.convert_tokens_to_string(qa_tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer

@app.route('/senseai/summarize', methods=['POST'])
def summarize():
    data = request.get_json()

    if 'request_data' not in data or 'folder_path' not in data['request_data']:
        return jsonify({"error": "request_data with folder_path is required"}), 400

    folder_path = data['request_data']['folder_path']
    
    try:
        summary = summarize_files(folder_path)
        
        # Check if summary is correctly generated
        if not summary:
            raise ValueError("No summary generated. Check if files have content.")
        
        # Saving the summary to a single PDF file
        output_dir = "/home/llm-01/chandana/outputsummary"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_pdf_path = save_summary_to_pdf(summary, output_dir)
        
        return jsonify({
            "summary_pdf_path": output_pdf_path,
            "summary_pdf_url": f"/download/{os.path.basename(output_pdf_path)}",
            "message": "Summary generated and saved successfully"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/senseai/query', methods=['POST'])
def query():
    data = request.get_json()

    if 'request_data' not in data or 'folder_path' not in data['request_data'] or 'query' not in data['request_data']:
        return jsonify({"error": "request_data with folder_path and query is required"}), 400

    folder_path = data['request_data']['folder_path']
    query_text = data['request_data']['query']
    
    try:
        file_contents = file_preprocessing(folder_path)
        file_texts = [file_data['file_text'] for file_data in file_contents]
        
        # Compute embeddings for all file texts and query
        file_embeddings = embedding_model.encode(file_texts, convert_to_tensor=True)
        query_embedding = embedding_model.encode(query_text, convert_to_tensor=True)
        
        # Find most relevant file using cosine similarity
        top_idx, similarity_score = query_embeddings(file_embeddings, query_embedding)
        most_relevant_file = file_contents[top_idx]
        
        # Answer the query using the most relevant file's text
        answer = answer_question(qa_model, qa_tokenizer, most_relevant_file['file_text'], query_text)
        
        return jsonify({
            "most_relevant_file": most_relevant_file['file_name'],
            "similarity_score": similarity_score,
            "answer": answer,
            "message": "Query answered successfully"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join("/home/llm-01/chandana/outputsummary", filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5007, debug=True)
