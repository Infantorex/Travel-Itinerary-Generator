# 🌍 Voyagr — AI Travel Itinerary Generator

<p align="center">
  <img title="Voyagr - AI Travel Itinerary Generator" src="/static/logo.svg" alt="Voyagr Logo" width="140"/>
</p>

<p align="center">
  <b>Plan your dream trips effortlessly with AI-powered personalized itineraries, real-time weather forecasting, dynamic translations, and instant PDF exports.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"/>
  <img src="https://img.shields.io/badge/Flask-3.1%2B-black.svg?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/AI-Google_GenAI-8E75B2.svg?style=for-the-badge&logo=google&logoColor=white" alt="Google GenAI"/>
  <img src="https://img.shields.io/badge/License-Apache_2.0-green.svg?style=for-the-badge" alt="License"/>
</p>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Setup & Installation](#-setup--installation)
- [Configuration (.env)](#-configuration-env)
- [Usage Guide](#-usage-guide)
- [Screenshots & UI](#-screenshots--ui)
- [License](#-license)

---

## 🌟 Overview

**Voyagr (Travel Itinerary Generator)** is a modern, full-stack AI web application designed to eliminate the stress of trip planning. By combining **Google Gemini AI** and **Visual Crossing Weather API**, Voyagr crafts day-by-day itineraries tailored to your dates, origin, destination, and budget, complete with interactive translation, weather outlooks, and print-ready PDF downloads.

---

## 🚀 Key Features

- 🧠 **AI-Powered Day-by-Day Itineraries:** Generates curated morning, afternoon, and evening activities with realistic budget estimates and local insider tips.
- 🌤️ **Live Weather Forecasts:** Fetches accurate weather predictions for your travel dates and destination.
- 🌐 **Multi-Language Translation:** Seamlessly translates generated travel plans into over a dozen languages on the fly using `deep-translator`.
- 📄 **Export to PDF & Print:** One-click PDF generation and print formatting for offline travel access.
- 🔒 **User Authentication:** Secure user registration, bcrypt hashed passwords, and session management with SQLite / SQLAlchemy.
- 🎨 **Modern Glassmorphic UI:** Built with dark mode aesthetics, vibrant accents, smooth CSS transitions, and mobile responsiveness.
- ⚡ **Offline & API Fallback Mode:** Built-in intelligent fallback itinerary engine ensures uninterrupted usability even without active API keys.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask 3.1, Flask-SQLAlchemy, Werkzeug, Bcrypt
- **AI & Data:** Google GenAI SDK (`google-genai`), Visual Crossing Weather API, Deep-Translator
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** HTML5, CSS3 (Modern Glassmorphism & Custom Properties), Vanilla JavaScript, FontAwesome 6, Bootstrap 5.3
- **Tools & Utilities:** Python-Dotenv, Gunicorn, HTML2PDF, Markdown-it

---

## 📋 Prerequisites

Make sure you have the following installed on your system:
- **Python 3.10** or higher
- **Git**

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Infantorex/<YOUR-REPO-NAME>.git
cd Travel-Itinerary-Generator-main
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows (PowerShell / Command Prompt)
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration (.env)

Create a `.env` file in the root directory of the project and add your API keys:

```env
# Google AI Studio API Key (https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Visual Crossing Weather API Key (https://www.visualcrossing.com/weather-api)
WEATHER_API_KEY=your_weather_api_key_here

# Flask Secret Key for session encryption
SECRET_KEY=your_secure_random_secret_key
```

> [!TIP]
> If `GEMINI_API_KEY` or `WEATHER_API_KEY` is not provided, the application will automatically activate its smart fallback generator so you can test the entire workflow offline.

---

## 💻 Usage Guide

### Start the Application
Run the application using:
```bash
python wsgi.py
```
or
```bash
python app.py
```

Open your browser and visit:
👉 **`http://127.0.0.1:5000`** (or `http://localhost:5000`)

---

## 📸 Screenshots & UI

| Landing & Itinerary Planner | Generated Itinerary View |
|:---:|:---:|
| Modern Glassmorphic Search UI | Day-wise plans, weather outlook & PDF export |

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.
