# 📚 Smart Flashcards - AI-Powered Learning Assistant

Transform any PDF into intelligent flashcards with spaced repetition. Built with Streamlit and Google Gemini AI.

## 🌟 Live Demo

**[Click Here to Try the App](https://flashcard-app-py.streamlit.app/)**

> ⚡ **Note:** First load may take 30-40 seconds (free tier cold start). Enter your Gemini API key in the sidebar to start!

## ✨ Features

- 📄 **Upload Any PDF** - Extract text automatically
- 🤖 **AI-Generated Flashcards** - 20-25 comprehensive cards per document
- 🎯 **Spaced Repetition** - SM-2 algorithm for optimal learning
- 👆 **Swipe Interface** - Easy (swipe left) / Hard (swipe right)
- 🔄 **Smart Review** - Hard cards reappear until mastered
- 📊 **Progress Tracking** - Real-time mastery stats
- 📱 **Responsive Design** - Works on mobile, tablet, desktop
- 💎 **Glassmorphism UI** - Premium visual experience
- 📥 **PDF Export** - Download your flashcard decks

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone repository
git clone https://github.com/dikshakatiyar/flashcard-app-py.git
cd flashcard-app-py

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run the app
streamlit run app.py
