from flask import Flask, request, render_template, jsonify
import re
import pdfplumber
from docx import Document
import os

app = Flask(__name__)

# Functions wahi rahenge jo pehle thi
def extract_text_from_resume(file_path):
    # ... (same function as before)

def extract_skills(resume_text):
    # ... (same function as before)

def suggest_jobs(found_skills, job_db):
    # ... (same function as before)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    # Save file temporarily
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    
    # Process file
    resume_text = extract_text_from_resume(file_path)
    skills = extract_skills(resume_text)
    jobs = suggest_jobs(skills, JOB_DATABASE)
    
    # Clean up
    os.remove(file_path)
    
    return jsonify({'skills': skills, 'jobs': jobs})

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)