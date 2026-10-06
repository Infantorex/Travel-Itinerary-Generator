from deep_translator import GoogleTranslator
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_sitemapper import Sitemapper
import bcrypt
import requests
import datetime
import bard, os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()
api_key = os.environ.get("WEATHER_API_KEY")
secret_key = os.environ.get("SECRET_KEY", "voyagr-travel-generator-secret-2026")

# Initialize base directories for reliable template/static resolution on Vercel & local
base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, 'templates'),
    static_folder=os.path.join(base_dir, 'static')
)
sitemapper = Sitemapper(app=app) # Create and initialize the sitemapper

# Database configuration: support DATABASE_URL, Vercel /tmp, or local SQLite
is_vercel = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Handle postgres:// to postgresql:// for modern SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
elif is_vercel:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/database.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = secret_key


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'), self.password.encode('utf8'))


with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"DB init warning: {e}")

@app.after_request
def add_csp_header(response):
    csp = (
        "default-src 'self'; "
        # Allow external scripts like FontAwesome, Bootstrap, EmailJS, markdown-it, html2pdf
        "script-src 'self' 'unsafe-inline' https://kit.fontawesome.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://emailjs.com; "
        # Allow inline styles and external stylesheets (Bootstrap, FontAwesome, Google Fonts)
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        # Allow fonts from Google Fonts and jsDelivr
        "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        # Allow images from same origin, data URIs, and Unsplash
        "img-src 'self' data: https://images.unsplash.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        # Allow external connections for emailjs, translator
        "connect-src 'self' https://emailjs.com https://api.emailjs.com; "
        "frame-src 'none'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "manifest-src 'self'; "
        "media-src 'self'; "
        "worker-src 'self'; "
    )
    response.headers['Content-Security-Policy'] = csp
    return response

# Weather Data Helper
def generate_fallback_weather_data(location: str, start_date: str, end_date: str) -> dict:
    """Generates realistic weather forecast data when API key is missing or offline."""
    try:
        s_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        e_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except Exception:
        s_date = datetime.datetime.now()
        e_date = s_date + datetime.timedelta(days=4)

    total_days = max(1, (e_date - s_date).days + 1)
    sample_conditions = [
        {"conditions": "Sunny & Pleasant", "tempmax": 28.5, "tempmin": 19.2, "precipprob": 5, "humidity": 52, "description": "Clear skies with pleasant gentle breeze, ideal for sightseeing."},
        {"conditions": "Partly Cloudy", "tempmax": 27.0, "tempmin": 18.8, "precipprob": 15, "humidity": 58, "description": "Scattered clouds with comfortable mild temperatures throughout the day."},
        {"conditions": "Mostly Sunny", "tempmax": 29.2, "tempmin": 20.1, "precipprob": 10, "humidity": 55, "description": "Warm and bright sunny intervals throughout the afternoon."},
        {"conditions": "Light Afternoon Showers", "tempmax": 26.4, "tempmin": 18.0, "precipprob": 40, "humidity": 68, "description": "Brief refreshing passing shower in the afternoon, clear evening."},
        {"conditions": "Clear Skies", "tempmax": 28.0, "tempmin": 19.5, "precipprob": 0, "humidity": 50, "description": "Unobstructed sunshine and crystal clear visibility."},
        {"conditions": "Breezy & Mild", "tempmax": 25.8, "tempmin": 17.5, "precipprob": 20, "humidity": 60, "description": "Cool gentle breeze with comfortable walking weather."},
        {"conditions": "Sunny & Warm", "tempmax": 30.1, "tempmin": 21.0, "precipprob": 10, "humidity": 48, "description": "Bright sunny day, sunscreen and sunglasses recommended."}
    ]

    days_data = []
    for i in range(total_days):
        day_date = s_date + datetime.timedelta(days=i)
        sample = sample_conditions[i % len(sample_conditions)]
        days_data.append({
            "datetime": day_date.strftime("%Y-%m-%d"),
            "conditions": sample["conditions"],
            "tempmax": sample["tempmax"],
            "tempmin": sample["tempmin"],
            "precipprob": sample["precipprob"],
            "humidity": sample["humidity"],
            "description": sample["description"]
        })

    return {
        "resolvedAddress": location,
        "days": days_data
    }

def get_weather_data(api_key: str, location: str, start_date: str, end_date: str) -> dict:
    """
    Retrieves weather data from Visual Crossing Weather API for a given location and date range.
    Falls back gracefully if API key is not configured or call fails.
    """
    if not api_key or api_key.strip() == "" or api_key.startswith("Your"):
        return generate_fallback_weather_data(location, start_date, end_date)

    base_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}?unitGroup=metric&include=days&key={api_key}&contentType=json"

    try:
        response = requests.get(base_url, timeout=8)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print("Weather API notice (using fallback):", e)
        return generate_fallback_weather_data(location, start_date, end_date)


@sitemapper.include() # Include the route in the sitemap
@app.route('/', methods=["GET", "POST"])
def index():
    """
    Renders the landing page and handles itinerary generation requests.
    """
    if request.method == "POST":
        source = (request.form.get("source") or "").strip()
        destination = (request.form.get("destination") or "").strip()
        start_date = request.form.get("date")
        end_date = request.form.get("return")

        if not source or not destination or not start_date or not end_date:
            flash("Please fill in all the required fields (Source, Destination, and Dates).", "danger")
            return redirect(url_for("index"))

        try:
            s_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            e_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            no_of_day = (e_dt - s_dt).days + 1
        except Exception:
            flash("Invalid date format entered. Please pick dates using the calendar.", "danger")
            return redirect(url_for("index"))

        if no_of_day < 1:
            flash("Return date must be on or after the Start date.", "danger")
            return redirect(url_for("index"))

        weather_data = get_weather_data(api_key, destination, start_date, end_date)

        try:
            plan = bard.generate_itinerary(source, destination, start_date, end_date, no_of_day)
        except Exception as e:
            flash("Error in generating the plan. Please try again later.", "danger")
            return redirect(url_for("index"))

        languages = GoogleTranslator().get_supported_languages(as_dict=True)
        return render_template(
            "dashboard.html",
            source=source,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            no_of_day=no_of_day,
            weather_data=weather_data,
            plan=plan,
            languages=languages
        )

    return render_template('index.html')


@sitemapper.include()
@app.route("/about")
def about():
    """Renders the about.html template."""
    return render_template("about.html")


@sitemapper.include()
@app.route("/contact")
def contact():
    """Renders the contact.html template."""
    user_email = session.get('user_email', "")
    user_name = session.get('user_name', "")
    return render_template("contact.html", user_email=user_email, user_name=user_name)


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """
    Translation endpoint used by the dashboard to translate itinerary and
    page text on demand. Supports both single string and list payloads.
    """
    data = request.get_json(silent=True) or {}
    target_lang = (data.get("target_lang") or "").strip().lower()
    texts = data.get("texts")
    text = (data.get("text") or "").strip()

    if (not text and not texts) or not target_lang:
        return jsonify({"error": "Missing text(s) or target language."}), 400

    def translate_single_text(cleaned: str) -> str:
        if not cleaned:
            return ""
        # 1. Try GoogleTranslator
        try:
            gt = GoogleTranslator(source="auto", target=target_lang)
            if len(cleaned) <= 4500:
                res = gt.translate(cleaned)
                if res:
                    return res
        except Exception:
            pass

        # 2. Try Gemini translation if client configured
        try:
            client = bard.get_client()
            if client:
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Translate the following travel text accurately into language code '{target_lang}'. Output ONLY the translated text without commentary:\n\n{cleaned}"
                )
                if resp and resp.text:
                    return resp.text.strip()
        except Exception:
            pass

        # 3. Return original text gracefully
        return cleaned

    if isinstance(texts, list):
        translated_items = []
        for item in texts:
            item_text = (item or "").strip()
            translated_items.append(translate_single_text(item_text) if item_text else "")
        return jsonify({"translated_texts": translated_items})

    translated = translate_single_text(text)
    return jsonify({"translated_text": translated})



@sitemapper.include()
@app.route("/login", methods=["GET", "POST"])
def login():
    """Renders login page and authenticates users."""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            flash("Welcome back! Login successful.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password. Please check credentials or register.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")


@sitemapper.include()
@app.route("/logout")
def logout():
    """Logs the user out."""
    session.clear()
    flash("You have been logged out safely.", "info")
    return redirect(url_for("index"))


@sitemapper.include()
@app.route("/register", methods=["GET", "POST"])
def register():
    """Renders register page and handles user sign up."""
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        password2 = request.form.get("password2") or ""

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != password2:
            flash("Passwords do not match. Please re-enter.", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter((User.email == email) | (User.name == name)).first()
        if existing_user:
            flash("An account with this email or username already exists. Please log in.", "danger")
            return redirect(url_for("login"))

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_email"] = user.email
        flash("Registration successful! Welcome to Voyagr.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route('/robots.txt')
def robots():
    return render_template('robots.txt')


@app.route("/sitemap.xml")
def r_sitemap():
    return sitemapper.generate()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}


if __name__ == '__main__':
    app.run(debug=True, port=5000)
