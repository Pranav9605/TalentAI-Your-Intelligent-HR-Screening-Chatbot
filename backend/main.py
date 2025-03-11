# backend/main.py

import os
import re
import requests
from typing import List, Dict

import spacy
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (GOOGLE_API_KEY)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.0-flash"

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

app = FastAPI(title="HR Chatbot API")

# Global variable to store the uploaded Job Description (JD)
JOB_DESCRIPTION = ""

# ---------------------------
# Data Models
# ---------------------------
class ChatRequest(BaseModel):
    message: str

class SegmentResponse(BaseModel):
    segment: str
    intents: List[str]
    responses: Dict[str, str]

class ChatResponse(BaseModel):
    segments: List[SegmentResponse]

# ---------------------------
# Endpoint to Upload Job Description
# ---------------------------
@app.post("/upload_jd")
async def upload_jd(file: UploadFile = File(...)):
    global JOB_DESCRIPTION
    content = await file.read()
    JOB_DESCRIPTION = content.decode("utf-8")
    return {"message": "Job description uploaded successfully."}

# ---------------------------
# NLP Utility Functions
# ---------------------------
def segment_intents(message: str) -> List[str]:
    """
    Splits a user message into segments based on conjunctions such as 'and', 'then', or 'but'.
    """
    doc = nlp(message)
    segments = []
    current_segment = []
    for token in doc:
        if token.lower_ in ["and", "then", "but"]:
            if current_segment:
                segment_text = " ".join([t.text for t in current_segment]).strip()
                if segment_text:
                    segments.append(segment_text)
                current_segment = []
        else:
            current_segment.append(token)
    if current_segment:
        segment_text = " ".join([t.text for t in current_segment]).strip()
        if segment_text:
            segments.append(segment_text)
    return segments

def multi_intent_classifier(segment: str) -> List[str]:
    """
    Detects intents in a segment using a rule‐based approach.
    If the segment contains job-related keywords, it returns ["hr"].
    Otherwise, if the segment looks like a question or greeting, it returns "qna" or "chitchat".
    """
    lower = segment.lower()
    hr_keywords = [
        "job", "position", "recruit", "hr", "resume", "interview",
        "experience", "qualification", "requirement", "skill"
    ]
    if any(word in lower for word in hr_keywords):
        return ["hr"]
    
    # If it's a question, mark as Q&A.
    intents = []
    if "?" in segment or any(word in lower for word in ["who", "what", "when", "where", "why", "how"]):
        intents.append("qna")
    # Default to chit-chat if nothing else.
    if any(word in lower for word in ["hello", "hi", "hey"]) or not intents:
        intents.append("chitchat")
    
    return list(set(intents))

# ---------------------------
# Response Generators
# ---------------------------
def get_gemini_response(message: str, role: str) -> str:
    """
    Generates a response using the Gemini model.
    The 'role' parameter determines the style (chitchat or qna).
    """
    if role == "chitchat":
        prompt = f"You are a friendly chat buddy. Engage in a light-hearted conversation: '{message}'"
    elif role == "qna":
        prompt = f"You are an intelligent assistant. Answer the question: '{message}'"
    else:
        prompt = message

    chat = genai.GenerativeModel(MODEL_NAME).start_chat(history=[])
    response = chat.send_message(prompt, stream=True)
    response_text = "".join(chunk.text for chunk in response)
    return response_text.strip()

def get_hr_response(segment: str) -> str:
    """
    Generates an HR screening response using the uploaded Job Description.
    If a JD is uploaded, the JD's full content is included in the prompt for context.
    """
    if not JOB_DESCRIPTION:
        return "Please upload a job description to get HR-related insights."
    
    prompt = (
        "You are an expert HR screening assistant. "
        "Below is the complete job description provided by the employer:\n\n"
        f"{JOB_DESCRIPTION}\n\n"
        "Based on the above job description, answer the following query with clear and detailed insights about the required experience, qualifications, and skills:\n"
        f"{segment}"
    )
    chat = genai.GenerativeModel(MODEL_NAME).start_chat(history=[])
    response = chat.send_message(prompt, stream=True)
    response_text = "".join(chunk.text for chunk in response)
    return response_text.strip()

# ---------------------------
# Unified Chat Endpoint
# ---------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    message = chat_request.message
    segments_text = segment_intents(message)
    segments_responses = []
    
    for segment in segments_text:
        intents = multi_intent_classifier(segment)
        responses = {}
        for intent in intents:
            if intent == "hr":
                responses["hr"] = get_hr_response(segment)
            elif intent == "qna":
                responses["qna"] = get_gemini_response(segment, role="qna")
            elif intent == "chitchat":
                responses["chitchat"] = get_gemini_response(segment, role="chitchat")
            else:
                responses[intent] = "No response available."
        segments_responses.append(SegmentResponse(segment=segment, intents=intents, responses=responses))
    return ChatResponse(segments=segments_responses)
