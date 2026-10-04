from google import genai
import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load the environment variables from the project root even if cwd differs
env_path = Path(__file__).resolve().with_name(".env")
load_dotenv(env_path)
api_key = os.environ.get("GEMINI_API_KEY")

# Initialize client lazily
_client = None

def get_client():
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY") or api_key
        if not key or key.strip() == "" or key.startswith("Your"):
            return None
        _client = genai.Client(api_key=key)
    return _client

def generate_fallback_itinerary(source, destination, start_date, end_date, no_of_days):
    """
    Provides a comprehensive, realistic travel itinerary if Gemini API key
    is not configured or offline.
    """
    days = max(1, no_of_days)
    itinerary_md = f"""# ✈️ Personalized Travel Itinerary: {destination}
**Origin:** {source} | **Dates:** {start_date} to {end_date} ({days} Days) | **Currency:** INR (₹)

---

## 🌟 Trip Overview & Highlights
Welcome to your tailor-made journey to **{destination}**! This curated itinerary is optimized for a balanced blend of iconic landmarks, cultural immersion, local gastronomy, and relaxing leisure.

---
"""
    for day_num in range(1, days + 1):
        itinerary_md += f"""
### 🗓️ Day {day_num}: Exploring {destination} — Highlights & Hidden Gems

- **🌅 Morning (08:30 AM – 12:00 PM):**
  - **Activity:** Breakfast at a recommended local café, followed by visiting the prime landmark or historic district of {destination}.
  - **Tip:** Arrive early to beat the crowd and enjoy prime photography lighting.
  - **Estimated Cost:** ₹500 – ₹1,200 per person.

- **☀️ Afternoon (12:30 PM – 04:30 PM):**
  - **Dining:** Authentic local specialty lunch at a top-rated traditional bistro/restaurant.
  - **Activity:** Guided walking tour, museum discovery, or local craft markets.
  - **Estimated Cost:** ₹800 – ₹1,800 per person.

- **🌇 Evening & Night (05:30 PM – 09:30 PM):**
  - **Activity:** Sunset viewpoints or riverside promenade stroll, followed by vibrant evening street markets.
  - **Dinner & Drinks:** Experiencing famous street food delicacies or rooftop dining with city vistas.
  - **Estimated Cost:** ₹1,000 – ₹2,500 per person.

---
"""

    itinerary_md += f"""
## 💰 Budget Breakdown Estimate (Per Person)
| Category | Daily Average (INR) | Total for {days} Days |
| :--- | :--- | :--- |
| **Accommodation (3-4 Star)** | ₹3,500 – ₹6,000 | ₹{days * 4500:,} |
| **Dining & Drinks** | ₹1,500 – ₹2,500 | ₹{days * 2000:,} |
| **Local Transport & Transit** | ₹600 – ₹1,200 | ₹{days * 900:,} |
| **Entry Tickets & Activities** | ₹800 – ₹1,500 | ₹{days * 1100:,} |
| **Estimated Total** | **₹6,400 – ₹11,200 / day** | **₹{days * 8500:,} (approx.)** |

---

## 🧳 Essential Travel Tips for {destination}
1. **Local Transit:** Utilize metro/subway cards or rideshare apps for the quickest and most economical city travel.
2. **Connectivity:** Pick up an eSIM or local prepaid SIM card upon arrival for seamless maps and translation access.
3. **Currency & Payments:** Most venues accept contactless cards and UPI/QR payments, but carrying ₹2,000–₹3,000 in cash is recommended for small vendors.
4. **Safety & Packing:** Keep a digital copy of your IDs, pack comfortable walking shoes, and stay hydrated throughout your exploration!
"""
    return itinerary_md

# Google Search grounding tool
grounding_tool = genai.types.Tool(
    google_search=genai.types.GoogleSearch()
)

def generate_itinerary(source, destination, start_date, end_date, no_of_days):
    system_prompt = (
        "You are an expert travel planner specializing in Indian and international trips. "
        "Always give detailed, practical, and budget-friendly itineraries. "
        "Ensure the tone is friendly, informative, and concise. "
        "Use INR for all costs, and include real, popular attractions and dining options. "
        "Format with clear Markdown headings, emojis, bullet points, and a budget table."
    )
    user_prompt = (
        f"Generate a personalized {no_of_days}-day trip itinerary "
        f"from {source} to {destination} between {start_date} and {end_date}. "
        f"Include sightseeing, food recommendations, transport suggestions, "
        f"and an optimum budget per day in INR formatted cleanly in markdown with a summary table."
    )

    try:
        client = get_client()
        if client is None:
            return generate_fallback_itinerary(source, destination, start_date, end_date, no_of_days)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                tools=[grounding_tool], 
                system_instruction=[system_prompt]
            )
        )
        if response and response.text:
            return response.text
        return generate_fallback_itinerary(source, destination, start_date, end_date, no_of_days)
    except Exception as e:
        print(f"Gemini API Exception: {e}")
        return generate_fallback_itinerary(source, destination, start_date, end_date, no_of_days)