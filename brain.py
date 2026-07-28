import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    gemma_models = [m for m in available_models if 'gemma' in m.lower()]
    chosen_model_name = gemma_models[0] if gemma_models else 'models/gemini-1.5-flash'
    model = genai.GenerativeModel(chosen_model_name)
except Exception as e:
    print(f"Model Error: {e}")

class IntelligenceBrain:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.knowledge_chunks = []
        self.load_and_process_pdf()

    def load_and_process_pdf(self):
        try:
            loader = PyPDFLoader(self.pdf_path)
            pages = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            self.knowledge_chunks = text_splitter.split_documents(pages)
        except Exception as e:
            print(f"PDF Error: {e}")

    def analyze_live_violation(self, image_path, is_danger_zone):
        context = "\n".join([doc.page_content for doc in self.knowledge_chunks[:3]])
        zone_status = "IN RESTRICTED BLAST ZONE" if is_danger_zone else "IN SAFE ZONE"
        
        prompt = f"""
        You are the Guardian Eye AI. 
        SITUATION: Person detected. ZONE: {zone_status}.
        RULES: {context}
        
        1. If in RESTRICTED ZONE -> Priority: CRITICAL, Msg: "ARENA INTRUSION", Reason: "Person in blast radius".
        2. If missing safety gear/tools -> Priority: COMPLIANCE, Msg: "SAFETY VIOLATION", Reason: "Missing PPE/Tools".
        
        RESPONSE FORMAT (STRICT JSON):
        {{
            "priority": "CRITICAL" or "COMPLIANCE",
            "msg": "...",
            "reason": "...",
            "identity": "EMP_AUTO_DETECT"
        }}
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except:
            return '{"priority": "COMPLIANCE", "msg": "Scanning", "reason": "AI Processing", "identity": "SYS"}'