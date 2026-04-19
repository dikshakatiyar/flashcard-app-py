# app.py - Premium Flashcard App with Glossy Effects

import streamlit as st
import json
import os
import random
import time
from datetime import datetime
from dotenv import load_dotenv
import pdfplumber
import requests
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import io

load_dotenv()

st.set_page_config(
    page_title="Smart Flashcards",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS with Glossy Glass Effects
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Premium Color Palette */
    :root {
        --crimson-dark: #8B0000;
        --crimson: #DC143C;
        --crimson-light: #FF6B6B;
        --cream-dark: #E8DCC8;
        --cream: #FFF5E6;
        --cream-light: #FFFBF5;
        --warm-brown: #8B6914;
        --gold: #DAA520;
        --dark-bg: #2C1810;
    }
    
    /* Main Container */
    .stApp {
        background: linear-gradient(135deg, #FFF5E6 0%, #F5E6D3 50%, #FFF5E6 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom Header with Glass Effect */
    .premium-header {
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 50%, #8B0000 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 30px 30px;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 10px 30px rgba(139, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translate(-30%, -30%) rotate(0deg); }
        100% { transform: translate(30%, 30%) rotate(360deg); }
    }
    
    .premium-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .premium-header p {
        color: rgba(255,255,255,0.95);
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Flashcard - Glass Effect Restored */
    .flashcard-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 500px;
        margin: 2rem auto;
        max-width: 650px;
    }
    
    .flashcard {
        background: linear-gradient(135deg, rgba(255, 251, 245, 0.95) 0%, rgba(255, 245, 230, 0.95) 100%);
        backdrop-filter: blur(10px);
        width: 100%;
        max-width: 600px;
        min-height: 420px;
        border-radius: 28px;
        padding: 2rem;
        box-shadow: 0 20px 40px -12px rgba(139, 0, 0, 0.25);
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        border: 2px solid rgba(220, 20, 60, 0.2);
        margin: 0 auto;
        overflow: hidden;
    }
    
    .flashcard::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #8B0000, #DC143C, #FF6B6B, #DC143C, #8B0000);
        border-radius: 28px 28px 0 0;
    }
    
    .flashcard::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .flashcard:hover::after {
        opacity: 1;
    }
    
    .flashcard:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 30px 50px -15px rgba(139, 0, 0, 0.35);
        border-color: rgba(220, 20, 60, 0.4);
    }
    
    .question-text {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #2C1810;
        line-height: 1.4;
        text-align: center;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 1;
    }
    
    .answer-text {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #4A3B2C;
        line-height: 1.6;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 2px solid rgba(220, 20, 60, 0.2);
        text-align: left;
        background: rgba(255, 245, 230, 0.8);
        backdrop-filter: blur(5px);
        padding: 1.2rem;
        border-radius: 16px;
    }
    
    /* Stats Cards - Glass Effect */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card-premium {
        background: rgba(255, 251, 245, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid rgba(220, 20, 60, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .stat-card-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(220, 20, 60, 0.1), transparent);
        transition: left 1s ease;
    }
    
    .stat-card-premium:hover::before {
        left: 100%;
    }
    
    .stat-card-premium:hover {
        transform: translateY(-25px);
        box-shadow: 0 12px 25px rgba(139, 0, 0, 0.15);
        border-color: rgba(220, 20, 60, 0.4);
        background: rgba(255, 251, 245, 1);
    }
    
    .stat-number-premium {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label-premium {
        color: #8B6914;
        font-size: 0.8rem;
        margin-top: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Buttons with Glass Effect */
    .stButton button {
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(139, 0, 0, 0.4);
    }
    
    /* Sidebar with Glass Effect */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(44, 24, 16, 0.95) 0%, rgba(26, 15, 10, 0.95) 100%);
        backdrop-filter: blur(10px);
        border-right: 2px solid #DC143C;
    }
    
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #FFF5E6 !important;
    }
    
    /* File Uploader with Glass Effect */
    [data-testid="stFileUploader"] {
        background: rgba(255, 245, 230, 0.9);
        backdrop-filter: blur(10px);
        border: 2px dashed #DC143C;
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        background: rgba(255, 245, 230, 1);
        border-color: #8B0000;
        transform: scale(1.02);
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #DC143C !important;
        color: white !important;
    }
    
    /* Text Input with Glass Effect */
    .stTextInput input {
        background: rgba(255, 245, 230, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid #DC143C;
        border-radius: 8px;
        color: #2C1810;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        background: rgba(255, 245, 230, 1);
        border-color: #8B0000;
        box-shadow: 0 0 10px rgba(220, 20, 60, 0.3);
        transform: scale(1.01);
    }
    
    .stTextInput label {
        color: #2C1810 !important;
        font-weight: 600;
    }
    
    /* Progress Section with Glass Effect */
    .progress-section-premium {
        background: rgba(255, 251, 245, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(220, 20, 60, 0.2);
        transition: all 0.3s ease;
    }
    
    .progress-section-premium:hover {
        background: rgba(255, 251, 245, 1);
        box-shadow: 0 5px 20px rgba(139, 0, 0, 0.1);
    }
    
    .progress-label-premium {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        color: #2C1810;
        font-weight: 600;
    }
    
    .progress-track-premium {
        background: rgba(220, 20, 60, 0.1);
        border-radius: 20px;
        height: 10px;
        overflow: hidden;
    }
    
    .progress-fill-premium {
        background: linear-gradient(90deg, #8B0000, #DC143C);
        height: 100%;
        transition: width 0.5s ease;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
    }
    
    .progress-fill-premium::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: progressShimmer 2s infinite;
    }
    
    @keyframes progressShimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Welcome Section - Glass Effect Restored */
    .welcome-premium {
        text-align: center;
        padding: 3rem;
        background: rgba(255, 251, 245, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        margin: 2rem;
        border: 2px solid rgba(220, 20, 60, 0.2);
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-premium::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(220, 20, 60, 0.05) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .welcome-premium:hover {
        transform: translateY(-5px);
        background: rgba(255, 251, 245, 1);
        box-shadow: 0 20px 40px rgba(139, 0, 0, 0.15);
        border-color: rgba(220, 20, 60, 0.4);
    }
    
    .welcome-premium h1 {
        color: #8B0000;
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        margin-top: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .welcome-premium p {
        color: #8B6914;
        font-size: 1rem;
        position: relative;
        z-index: 1;
    }
    
    /* Deck Cards with Glass Effect */
    .deck-card-premium {
        background: rgba(255, 245, 230, 0.15);
        backdrop-filter: blur(5px);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid rgba(220, 20, 60, 0.3);
    }
    
    .deck-card-premium:hover {
        background: rgba(220, 20, 60, 0.2);
        transform: translateX(5px);
        border-color: #DC143C;
    }
    
    /* Simple Symbols */
    .symbol {
        font-size: 3rem;
        color: #8B0000;
        display: inline-block;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    /* Animations */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes shuffle {
        0% { transform: rotate(0deg) translateX(0); opacity: 0; }
        25% { transform: rotate(5deg) translateX(20px); opacity: 0.3; }
        50% { transform: rotate(-5deg) translateX(-20px); opacity: 0.6; }
        75% { transform: rotate(3deg) translateX(10px); opacity: 0.8; }
        100% { transform: rotate(0deg) translateX(0); opacity: 1; }
    }
    
    .fade-in {
        animation: slideIn 0.5s ease-out;
    }
    
    .shuffle-animation {
        animation: shuffle 0.6s ease-in-out;
    }
    
    /* Glass Panel */
    .glass-panel {
        background: rgba(255, 251, 245, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(220, 20, 60, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'decks' not in st.session_state:
    st.session_state.decks = {}
if 'current_deck' not in st.session_state:
    st.session_state.current_deck = None
if 'current_cards' not in st.session_state:
    st.session_state.current_cards = []
if 'card_index' not in st.session_state:
    st.session_state.card_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'hard_cards' not in st.session_state:
    st.session_state.hard_cards = []
if 'mastered_cards' not in st.session_state:
    st.session_state.mastered_cards = []
if 'session_active' not in st.session_state:
    st.session_state.session_active = False
if 'shuffling' not in st.session_state:
    st.session_state.shuffling = False

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for i, page in enumerate(pdf.pages[:15]):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text[:8000]

def generate_flashcards(text, api_key):
    """Generate flashcards with proper error handling"""
    prompt = f"""You are an expert educator. Create 20-25 comprehensive flashcards from this text.

Requirements:
- Questions should test deep understanding
- Answers must be detailed (3-5 sentences with examples)
- Include definitions, relationships, applications

Output ONLY JSON array. Do not add any other text before or after.
Example response format:
[
  {{"question": "What is X and why is it important?", "answer": "X is defined as Y. It is important because Z."}},
  {{"question": "How does Y work?", "answer": "Y works by doing A, B, and C."}}
]

Text to convert:
{text[:6000]}

Now, output ONLY the JSON array with no additional text:"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 16384,
            "topP": 0.95
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        
        # Check if request was successful
        if response.status_code != 200:
            error_detail = response.text
            raise Exception(f"API Error {response.status_code}: {error_detail[:200]}")
        
        result = response.json()
        
        # Debug: Print response structure (remove in production)
        # st.write("API Response Keys:", result.keys())
        
        # Handle different response structures
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                response_text = candidate['content']['parts'][0]['text']
            else:
                raise Exception("Unexpected response structure: missing content/parts")
        else:
            raise Exception(f"No candidates in response. Response: {str(result)[:200]}")
        
        # Extract JSON from response
        json_match = re.search(r'\[\s*\{.*?\}\s*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            # Try to find any array
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise Exception(f"No JSON array found in response: {response_text[:200]}")
        
        # Clean up
        json_str = json_str.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        flashcards = json.loads(json_str)
        
        if not isinstance(flashcards, list):
            flashcards = [flashcards]
        
        # Validate and clean flashcards
        valid = []
        for card in flashcards:
            if isinstance(card, dict):
                question = card.get('question', '').strip()
                answer = card.get('answer', '').strip()
                if question and answer:
                    valid.append({
                        'question': question,
                        'answer': answer
                    })
        
        if not valid:
            # Fallback: Create a simple flashcard from the text
            valid = [{
                'question': f"Summarize the key points from the text: {text[:100]}...",
                'answer': f"The text covers: {text[:300]}..."
            }]
        
        return valid
    
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"Generation failed: {str(e)}")

def create_pdf_export(flashcards, deck_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#8B0000'), alignment=1, spaceAfter=30)
    card_title_style = ParagraphStyle('CardTitle', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#DC143C'), spaceAfter=12, spaceBefore=20)
    question_style = ParagraphStyle('Question', parent=styles['Normal'], fontSize=12, leftIndent=20, rightIndent=20, spaceAfter=10)
    answer_style = ParagraphStyle('Answer', parent=styles['Normal'], fontSize=11, leftIndent=40, rightIndent=20, spaceAfter=20, backColor=colors.HexColor('#FFF5E6'))
    
    story = []
    story.append(Paragraph(f"Flashcards: {deck_name}", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle('Date', parent=styles['Normal'], alignment=1)))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Total Cards: {len(flashcards)}", ParagraphStyle('Count', parent=styles['Normal'], alignment=1)))
    story.append(Spacer(1, 0.5 * inch))
    
    for i, card in enumerate(flashcards, 1):
        story.append(Paragraph(f"<b>Flashcard #{i}</b>", card_title_style))
        story.append(Paragraph(f"<b>Question:</b><br/>{card['question']}", question_style))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(f"<b>Answer:</b><br/>{card['answer']}", answer_style))
        story.append(Spacer(1, 0.2 * inch))
        if i < len(flashcards):
            story.append(PageBreak())
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Sidebar
with st.sidebar:
    st.markdown("## 📚 YOUR LIBRARY")
    st.markdown("---")
    
    if st.session_state.decks:
        for deck_name in list(st.session_state.decks.keys()):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"📖 {deck_name}", key=f"select_{deck_name}", use_container_width=True):
                    st.session_state.current_deck = deck_name
                    st.session_state.session_active = False
                    st.session_state.current_cards = []
                    st.session_state.card_index = 0
                    st.session_state.hard_cards = []
                    st.session_state.mastered_cards = []
                    st.rerun()
            with col2:
                if st.button("✕", key=f"del_{deck_name}"):
                    del st.session_state.decks[deck_name]
                    if st.session_state.current_deck == deck_name:
                        st.session_state.current_deck = None
                    st.rerun()
    else:
        st.info("✨ No decks yet. Create your first deck below!")
    
    st.markdown("---")
    st.markdown("## 📤 CREATE DECK")
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    deck_name = st.text_input("Deck name", placeholder="e.g., Machine Learning, History Chapter 5")
    
    if uploaded_file and deck_name:
        if st.button("✨ Generate Flashcards", type="primary", use_container_width=True):
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error("❌ GEMINI_API_KEY not found in .env file")
            else:
                with st.spinner("📖 Generating 20-25 detailed flashcards..."):
                    try:
                        text = extract_text_from_pdf(uploaded_file)
                        flashcards = generate_flashcards(text, api_key)
                        
                        if flashcards:
                            st.session_state.decks[deck_name] = flashcards
                            st.session_state.current_deck = deck_name
                            st.success(f"✅ Generated {len(flashcards)} flashcards!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 💡 TIPS")
    st.markdown("""
    • Easy → Card mastered  
    • Hard → Review later  
    • Reveal → Check answer  
    • PDF → Export deck
    """)

# Main content
if st.session_state.current_deck is None:
    st.markdown("""
    <div class="welcome-premium">
        <div class="symbol">📚</div>
        <h1>Smart Flashcards</h1>
        <p>Transform any PDF into intelligent flashcards with spaced repetition</p>
        <div class="stats-grid" style="max-width: 600px; margin: 2rem auto;">
            <div class="stat-card-premium">
                <div class="stat-number-premium">20-25</div>
                <div class="stat-label-premium">Cards per deck</div>
            </div>
            <div class="stat-card-premium">
                <div class="stat-number-premium">📖</div>
                <div class="stat-label-premium">Detailed answers</div>
            </div>
            <div class="stat-card-premium">
                <div class="stat-number-premium">🔄</div>
                <div class="stat-label-premium">Smart review</div>
            </div>
            <div class="stat-card-premium">
                <div class="stat-number-premium">📄</div>
                <div class="stat-label-premium">PDF export</div>
            </div>
        </div>
        <p>👈 Create a deck from the sidebar to begin your learning journey</p>
    </div>
    """, unsafe_allow_html=True)
else:
    deck_name = st.session_state.current_deck
    all_cards = st.session_state.decks.get(deck_name, [])
    
    if not all_cards:
        st.error("No cards in this deck.")
    else:
        # Header
        st.markdown(f"""
        <div class="premium-header">
            <h1>📚 {deck_name}</h1>
            <p>Master {len(all_cards)} flashcards with intelligent spaced repetition</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Start session
        if not st.session_state.session_active:
            cards_to_study = all_cards.copy()
            random.shuffle(cards_to_study)
            st.session_state.current_cards = cards_to_study
            st.session_state.card_index = 0
            st.session_state.hard_cards = []
            st.session_state.mastered_cards = []
            st.session_state.session_active = True
            st.session_state.shuffling = True
        
        # Shuffling animation
        if st.session_state.shuffling:
            st.markdown("""
            <div style="text-align: center; padding: 3rem;">
                <div class="shuffle-animation" style="background: rgba(255, 251, 245, 0.9); backdrop-filter: blur(10px); border-radius: 28px; padding: 2.5rem; max-width: 450px; margin: 0 auto; border: 2px solid rgba(220, 20, 60, 0.2);">
                    <div class="symbol" style="font-size: 4rem;">📚</div>
                    <h2 style="color: #8B0000; margin-top: 1rem;">Shuffling Your Deck...</h2>
                    <p style="color: #8B6914;">Preparing your learning journey</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.8)
            st.session_state.shuffling = False
            st.rerun()
        
        cards = st.session_state.current_cards
        idx = st.session_state.card_index
        
        # Calculate stats
        total_cards = len(all_cards)
        mastered_count = len(st.session_state.mastered_cards)
        hard_count = len(st.session_state.hard_cards)
        remaining = len(cards) - idx
        progress_percent = ((mastered_count + (idx - len(st.session_state.hard_cards))) / total_cards * 100) if total_cards > 0 else 0
        
        # Stats Dashboard
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card-premium">
                <div class="stat-number-premium">{total_cards}</div>
                <div class="stat-label-premium">Total Cards</div>
            </div>
            <div class="stat-card-premium">
                <div class="stat-number-premium">{mastered_count}</div>
                <div class="stat-label-premium">Mastered</div>
            </div>
            <div class="stat-card-premium">
                <div class="stat-number-premium">{hard_count}</div>
                <div class="stat-label-premium">For Review</div>
            </div>
            <div class="stat-card-premium">
                <div class="stat-number-premium">{remaining}</div>
                <div class="stat-label-premium">Remaining</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress section
        st.markdown(f"""
        <div class="progress-section-premium">
            <div class="progress-label-premium">
                <span>📈 Learning Progress</span>
                <span><strong>{progress_percent:.1f}%</strong> Complete</span>
            </div>
            <div class="progress-track-premium">
                <div class="progress-fill-premium" style="width: {progress_percent}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.75rem; color: #8B6914; font-size: 0.75rem;">
                <span>✓ {mastered_count} mastered</span>
                <span>⟳ {hard_count} to review</span>
                <span>📖 {remaining} remaining</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check session completion
        if idx >= len(cards):
            if hard_count > 0:
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem; background: rgba(255, 251, 245, 0.9); backdrop-filter: blur(10px); border-radius: 28px; margin: 2rem 0; border: 2px solid rgba(220, 20, 60, 0.2);">
                    <div class="symbol" style="font-size: 3rem;">⟳</div>
                    <h2 style="color: #8B0000; margin-top: 1rem;">Review Session</h2>
                    <p style="color: #8B6914;">You have <strong>{hard_count} cards</strong> that need more practice</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⟳ Review Hard Cards", use_container_width=True):
                        st.session_state.current_cards = st.session_state.hard_cards.copy()
                        st.session_state.card_index = 0
                        st.session_state.hard_cards = []
                        st.session_state.show_answer = False
                        st.rerun()
                with col2:
                    if st.button("✓ View Mastered Cards", use_container_width=True):
                        with st.expander("Mastered Cards"):
                            for i, card in enumerate(st.session_state.mastered_cards, 1):
                                st.markdown(f"**{i}. {card['question']}**")
                                st.caption(card['answer'][:200] + "...")
            else:
                st.balloons()
                st.markdown(f"""
                <div style="text-align: center; padding: 2.5rem; background: rgba(255, 251, 245, 0.9); backdrop-filter: blur(10px); border-radius: 28px; margin: 2rem 0; border: 2px solid rgba(220, 20, 60, 0.2);">
                    <div class="symbol" style="font-size: 4rem;">🏆</div>
                    <h1 style="color: #8B0000; margin-top: 1rem;">Congratulations!</h1>
                    <p style="color: #8B6914; font-size: 1.1rem;">You've mastered all {total_cards} flashcards!</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Practice Again", use_container_width=True):
                        st.session_state.session_active = False
                        st.rerun()
                with col2:
                    if st.button("📄 Export PDF", use_container_width=True):
                        pdf_bytes = create_pdf_export(all_cards, deck_name)
                        st.download_button("📥 Download PDF", pdf_bytes, f"{deck_name}_flashcards.pdf", "application/pdf")
        else:
            card = cards[idx]
            
            # Flashcard - Centered with better width
            st.markdown(f"""
            <div class="flashcard-container">
                <div class="flashcard fade-in">
                    <div class="question-text">
                        {card['question']}
                    </div>
                    <div style="text-align: center; margin-top: 1rem;">
                        <span style="color: #DC143C; font-size: 0.8rem;">▼ Tap anywhere to reveal answer ▼</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Answer section
            if st.session_state.show_answer:
                st.markdown(f"""
                <div style="max-width: 600px; margin: -1rem auto 0 auto;">
                    <div class="answer-text fade-in">
                        <strong>✓ Detailed Answer:</strong><br><br>
                        {card['answer']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("✓ EASY - Mastered", use_container_width=True):
                    st.session_state.mastered_cards.append(card)
                    st.session_state.card_index += 1
                    st.session_state.show_answer = False
                    st.rerun()
            
            with col2:
                if st.button("🔍 REVEAL ANSWER", use_container_width=True):
                    st.session_state.show_answer = True
                    st.rerun()
            
            with col3:
                if st.button("⟳ HARD - Review Later", use_container_width=True):
                    st.session_state.hard_cards.append(card)
                    st.session_state.card_index += 1
                    st.session_state.show_answer = False
                    st.rerun()
            
            # Export options
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Export PDF", use_container_width=True):
                    pdf_bytes = create_pdf_export(all_cards, deck_name)
                    st.download_button("📥 Download", pdf_bytes, f"{deck_name}_flashcards.pdf", "application/pdf")
            
            with col2:
                if st.button("🔄 New Session", use_container_width=True):
                    st.session_state.session_active = False
                    st.rerun()
            
            with col3:
                if st.button("🏠 Back to Library", use_container_width=True):
                    st.session_state.current_deck = None
                    st.session_state.session_active = False
                    st.rerun()