import streamlit as st
import pandas as pd
import spacy
from pdfminer.high_level import extract_text
import tempfile
import os

# Load SpaCy NLP model (English)
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    text = extract_text(tmp_path)
    os.remove(tmp_path)
    return text

# Function to analyze resume text
def analyze_resume(text):
    doc = nlp(text)
    name = None
    email = None
    phone = None
    skills = []

    # Extract entities
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not name:
            name = ent.text
        elif ent.label_ == "ORG":
            skills.append(ent.text)

    # Extract email and phone manually
    for token in doc:
        if "@" in token.text:
            email = token.text
        if token.like_num and len(token.text) >= 10:
            phone = token.text

    return {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Skills": ", ".join(set(skills)) if skills else "Not Found"
    }

# Streamlit UI
st.set_page_config(page_title="Smart Resume Analyzer", layout="wide")
st.title("📄 Smart Resume Analyzer")

uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Reading and analyzing resume..."):
        text = extract_text_from_pdf(uploaded_file)
        results = analyze_resume(text)

    st.subheader("Resume Analysis Result")
    df = pd.DataFrame([results])
    st.table(df)

    st.subheader("Extracted Text (Preview)")
    st.text_area("Resume Text", text[:2000], height=300)
