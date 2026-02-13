import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION ---
# Railway uses 'variables' to store secrets. We access them via os.environ.
API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key missing. Please add GOOGLE_API_KEY in Railway Variables.")
    st.stop()

# Configure the AI
genai.configure(api_key=API_KEY)
# Using Gemini 2.0 Flash (It is excellent at multilingual OCR/Reasoning)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- THE WEBPAGE LAYOUT ---
st.set_page_config(page_title="Document Reader", page_icon="📄")

st.title("📄 Document Reader")
st.write("Upload a document and ask questions in **English** or **Spanish**.")

# --- STEP 1: PDF UPLOADER ---
uploaded_file = st.file_uploader("Upload Document (PDF, PNG, JPG)", type=["pdf", "png", "jpg"])

# Check if a file is uploaded
if uploaded_file is not None:
    
    # --- STEP 2: HANDLE THE FILE ---
    # Save file temporarily so Gemini can upload it
    temp_filename = "temp_doc.pdf"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("✅ Document Loaded / Documento Cargado")

    # --- STEP 3: THE CHAT FORM ---
    with st.form(key='chat_form'):
        user_question = st.text_input("Ask a question (Pregunta lo que quieras):")
        submit_button = st.form_submit_button("Submit / Enviar")

    if submit_button and user_question:
        try:
            with st.spinner("Reading document / Leyendo documento..."):
                
                # 1. Upload the file to Gemini
                sample_file = genai.upload_file(path=temp_filename, display_name="User Upload")
                
                # 2. Define the Brain Rules (Updated for Spanish Support)
                system_prompt = """
                You are an intelligent Document Assistant capable of reading English and Spanish documents.
                
                RULES:
                1. **Language Detection**: Answer in the EXACT same language the user asks the question in.
                   - If the user asks in English -> Answer in English.
                   - If the user asks in Spanish -> Answer in Spanish.
                2. **Document Analysis**: You can read text in images, PDFs, and scans in any language. Analyze the content visible in the file.
                3. **Strictness**: Answer strictly based on the provided document. Do not hallucinate outside info.
                4. If the answer is not in the document, say "I cannot find that information" (translated to the language of the user).
                """
                
                # 3. Ask the Question
                response = model.generate_content([system_prompt, sample_file, user_question])
                
                # 4. Display Result
                st.write("### 🤖 Answer:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
