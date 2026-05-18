from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import joblib  
from fpdf import FPDF
import io

app = Flask(__name__)
# SECURITY KEY: Keep this secret
app.secret_key = 'healthcompass_sql_final_key'

# --- 1. LOAD THE TRAINED AI MODEL ---
try:
    model = joblib.load('health_model.pkl')
    print("AI Model loaded successfully!")
except:
    print("Error: Model not found. Please run train_model.py first.")
    model = None

# --- 2. DATABASE HELPER & INITIALIZATION ---
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    """Creates the necessary tables if they don't exist yet."""
    conn = get_db_connection()
    # Table 1: Users
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0
        )
    ''')
    # Table 2: History (NEW - To power the Dashboard)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            symptoms TEXT,
            diagnosis TEXT,
            advice TEXT,
            specialist TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Run this once when the app starts
init_db()

# --- 3. EXPANDED DATABASE OF ADVICE & SPECIALISTS ---
medical_db = {
    "Fungal infection": { "advice": "Keep area dry. Use antifungal cream. Bath twice daily.", "doctor": "Dermatologist" },
    "Acne": { "advice": "Avoid oily food. Wash face regularly. Don't pop pimples.", "doctor": "Dermatologist" },
    "Psoriasis": { "advice": "Use moisturizers. Avoid triggers like stress. Salt baths.", "doctor": "Dermatologist" },
    "Impetigo": { "advice": "Keep sores clean. Use antibiotic ointment. Remove scabs gently.", "doctor": "Dermatologist" },
    "Chicken pox": { "advice": "Do not scratch blisters. Use Calamine lotion. Isolate yourself.", "doctor": "General Physician" },
    "GERD": { "advice": "Avoid heavy meals before bed. Avoid fatty/spicy food.", "doctor": "Gastroenterologist" },
    "Peptic ulcer diseae": { "advice": "Avoid spicy food. Eat smaller meals. Eliminate alcohol.", "doctor": "Gastroenterologist" },
    "Jaundice": { "advice": "Drink plenty of water. Consume milk thistle. Eat fruits.", "doctor": "Gastroenterologist" },
    "Gastroenteritis": { "advice": "Stay hydrated. Eat bland foods (BRAT diet). Rest.", "doctor": "Gastroenterologist" },
    "Alcoholic hepatitis": { "advice": "Stop alcohol immediately. Consult doctor. Follow up.", "doctor": "Hepatologist" },
    "Hepatitis A": { "advice": "Consult hospital. Wash hands thoroughly. Avoid fatty food.", "doctor": "Hepatologist" },
    "Hepatitis B": { "advice": "Consult hospital. Vaccination. Eat healthy.", "doctor": "Hepatologist" },
    "Hepatitis C": { "advice": "Consult hospital. Vaccination. Eat healthy.", "doctor": "Hepatologist" },
    "Hepatitis D": { "advice": "Consult doctor. Medication. Eat healthy.", "doctor": "Hepatologist" },
    "Hepatitis E": { "advice": "Stop alcohol. Rest. Consult doctor.", "doctor": "Hepatologist" },
    "Chronic cholestasis": { "advice": "Cold baths. Anti-itch medicine. Eat healthy.", "doctor": "Hepatologist" },
    "Dimorphic hemmorhoids(piles)": { "advice": "Avoid fatty/spicy food. Warm baths. Consume fiber.", "doctor": "Proctologist" },
    "Hypertension ": { "advice": "Meditation. Reduce salt intake. Monitor BP regularly.", "doctor": "Cardiologist" },
    "Heart attack": { "advice": "Call ambulance immediately. Chew aspirin. Keep calm.", "doctor": "Cardiologist" },
    "Varicose veins": { "advice": "Wear compression stockings. Elevate legs. Don't stand still.", "doctor": "Vascular Surgeon" },
    "Migraine": { "advice": "Rest in a dark, quiet room. Meditation. Reduce stress.", "doctor": "Neurologist" },
    "Paralysis (brain hemorrhage)": { "advice": "Emergency condition. Massage. Eat healthy.", "doctor": "Neurologist" },
    "(vertigo) Paroymsal  Positional Vertigo": { "advice": "Lie down. Avoid sudden head movements. Relax.", "doctor": "Neurologist" },
    "Cervical spondylosis": { "advice": "Use heating pad. Exercise. Consult doctor.", "doctor": "Orthopedic" },
    "Bronchial Asthma": { "advice": "Use inhaler. Avoid dust/smoke. Take deep breaths.", "doctor": "Pulmonologist" },
    "Pneumonia": { "advice": "Rest. Antibiotics (if prescribed). Consult doctor.", "doctor": "Pulmonologist" },
    "Tuberculosis": { "advice": "Cover mouth. Complete medication course. Rest.", "doctor": "Pulmonologist" },
    "Diabetes ": { "advice": "Monitor blood sugar. Balanced diet. Exercise.", "doctor": "Endocrinologist" },
    "Hypothyroidism": { "advice": "Reduce stress. Exercise. Eat healthy.", "doctor": "Endocrinologist" },
    "Hyperthyroidism": { "advice": "Massage. Eat healthy. Monitor heart rate.", "doctor": "Endocrinologist" },
    "Hypoglycemia": { "advice": "Lie down. Drink sugary drinks. Check pulse.", "doctor": "Endocrinologist" },
    "Common Cold": { "advice": "Steam inhalation. Warm fluids. Rest.", "doctor": "General Physician" },
    "Dengue": { "advice": "Drink papaya leaf juice. Hydrate well. Keep mosquitoes away.", "doctor": "General Physician" },
    "Typhoid": { "advice": "Avoid outside food. Antibiotic therapy. Eat high calorie veg.", "doctor": "General Physician" },
    "Malaria": { "advice": "Use mosquito nets. Avoid oily food. Consult hospital.", "doctor": "General Physician" },
    "Viral Fever": { "advice": "Monitor body temperature. Take Paracetamol if > 100°F.", "doctor": "General Physician" },
    "AIDS": { "advice": "Avoid open cuts. Consult doctor. Follow up.", "doctor": "Infectious Disease Specialist" },
    "Urinary tract infection": { "advice": "Drink plenty of water. Cranberry juice. Increase vitamin C.", "doctor": "Urologist" },
    "Osteoarthristis": { "advice": "Acetaminophen. Hot/cold therapy. Salt baths.", "doctor": "Orthopedic" },
    "Arthritis": { "advice": "Exercise. Massage. Try acupuncture.", "doctor": "Rheumatologist" },
    "Allergy": { "advice": "Apply calamine. Cover area. Use ice compress.", "doctor": "Allergist" },
    "Drug Reaction": { "advice": "Stop taking drug. Stop irritation. Consult hospital.", "doctor": "General Physician" },
    "Asthma": {"advice": "Use inhaler. Avoid smoke and dust.", "doctor": "Pulmonologist"},
    "Common_Cold": {"advice": "Steam inhalation. Drink warm fluids.", "doctor": "General Physician"},
    "COVID_19": {"advice": "Isolate yourself. Monitor oxygen levels.", "doctor": "General Physician"},
    "Influenza": {"advice": "Rest well. Stay hydrated.", "doctor": "General Physician"}
}

# --- ROUTE: HOME ---
@app.route('/')
def home():
    user_info = session.get('user')
    return render_template('index.html', user=user_info)


# --- MOCK DOCTOR DATABASE ---
mock_doctors = {
    "Neurologist": [
        {"name": "Dr. A. Sharma", "clinic": "City Brain Clinic", "distance": "0.8 miles away", "time": "Available Today 3:00 PM"},
        {"name": "Dr. R. Verma", "clinic": "NeuroCare Center", "distance": "1.5 miles away", "time": "Available Tomorrow 10:00 AM"}
    ],
    "Cardiologist": [
        {"name": "Dr. S. Patil", "clinic": "Heart Institute", "distance": "1.2 miles away", "time": "Available Today 4:30 PM"},
        {"name": "Dr. K. Singh", "clinic": "Metro Hospital", "distance": "3.0 miles away", "time": "Available Tomorrow 9:00 AM"}
    ],
    "Gastroenterologist": [
        {"name": "Dr. M. Gupta", "clinic": "Digestive Health Clinic", "distance": "0.5 miles away", "time": "Available Today 1:00 PM"}
    ],
    "Dermatologist": [
        {"name": "Dr. L. Kumar", "clinic": "Skin & Glow Clinic", "distance": "2.1 miles away", "time": "Available Today 5:00 PM"}
    ],
    "General Physician": [
        {"name": "Dr. P. Joshi", "clinic": "Family Health Care", "distance": "0.3 miles away", "time": "Available Today 2:00 PM"},
        {"name": "Dr. N. Ali", "clinic": "City Hospital", "distance": "1.0 miles away", "time": "Available Today 6:00 PM"}
    ]
}

# --- ROUTE: DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
        
    email = session['user']
    conn = get_db_connection()
    
    user_data = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    history = conn.execute('SELECT * FROM history WHERE email = ? ORDER BY timestamp DESC', (email,)).fetchall()
    conn.close()
    
    # NEW LOGIC: Find doctors based on the MOST RECENT diagnosis
    recommended_doctors = []
    if history:
        # Get the specialist from the first (most recent) item in history
        latest_specialist = history[0]['specialist']
        # Fetch matching doctors, default to General Physician if specialist isn't in our mock DB
        recommended_doctors = mock_doctors.get(latest_specialist, mock_doctors.get("General Physician"))
    
    # Pass 'doctors' to the HTML template
    return render_template('dashboard.html', user=email, usage_count=user_data['usage_count'], history=history, doctors=recommended_doctors)

# --- ROUTE: ANALYZE SYMPTOMS ---
@app.route('/analyze', methods=['POST'])
def analyze_symptoms():

    if 'user' not in session:
        return jsonify({
            "status": "login_required",
            "message": "Please login to use AI."
        })

    current_user_email = session['user']

    data = request.json

    symptoms = data.get('symptoms', '').lower()

    # ---------------------------------------------------
    # CHECK TRIAL LIMIT
    # ---------------------------------------------------

    conn = get_db_connection()

    user = conn.execute(
        'SELECT * FROM users WHERE email = ?',
        (current_user_email,)
    ).fetchone()

    if user:

        usage = user['usage_count']

        if usage < 1 or usage < 0:

            if usage >= 0:
                conn.execute(
                    'UPDATE users SET usage_count = usage_count + 1 WHERE email = ?',
                    (current_user_email,)
                )

                conn.commit()

        else:

            conn.close()

            return jsonify({
                "status": "subscription_required",
                "message": "Free trial ended."
            })

    else:

        conn.close()

        return jsonify({
            "status": "error",
            "message": "User record not found."
        })

    # ---------------------------------------------------
    # AI PREDICTION ENGINE
    # ---------------------------------------------------

    diagnosis = "Unclear Symptoms"

    advice = "Please describe your symptoms in more detail."

    doctor = "General Physician"

    urgency = "Low"

    top_predictions = []

    # ---------------------------------------------------
    # URGENCY LEVELS
    # ---------------------------------------------------

    urgency_levels = {

        "Pneumonia": "High",
        "Dengue": "High",
        "Malaria": "High",

        "Asthma": "Emergency",

        "COVID_19": "Moderate",
        "Influenza": "Moderate",
        "Typhoid": "Moderate",
        "Migraine": "Moderate",
        "Diabetes": "Moderate",
        "Hypertension": "Moderate",
        "Food_Poisoning": "Moderate",
        "Gastroenteritis": "Moderate",

        "Common_Cold": "Low",
        "Allergic_Rhinitis": "Low",
        "Anxiety_Disorder": "Low"
    }

    # ---------------------------------------------------
    # MODEL PREDICTION
    # ---------------------------------------------------

    if model:

        probs = model.predict_proba([symptoms])[0]

        disease_names = model.classes_

        disease_probabilities = list(
            zip(disease_names, probs)
        )

        # Sort descending
        disease_probabilities.sort(
            key=lambda x: x[1],
            reverse=True
        )

        # Top 3 predictions
        top_3 = disease_probabilities[:3]

        # Normalize probabilities
        total_prob = sum(prob for _, prob in top_3)

        for disease, prob in top_3:

            normalized_prob = round(
                (prob / total_prob) * 100,
                2
            )

            top_predictions.append({
                "disease": disease,
                "probability": normalized_prob
            })

        # Main diagnosis
        diagnosis = top_predictions[0]["disease"]

        urgency = urgency_levels.get(
            diagnosis,
            "Moderate"
        )

        clean_pred = diagnosis.strip()

        # ---------------------------------------------------
        # ADVICE & DOCTOR RECOMMENDATION
        # ---------------------------------------------------

        if clean_pred in medical_db:

            advice = medical_db[clean_pred]["advice"]

            doctor = medical_db[clean_pred]["doctor"]

        else:

            advice = (
                "Please consult a healthcare professional "
                "for further evaluation."
            )

            doctor = "General Physician"

    # ---------------------------------------------------
    # FALLBACK LOGIC
    # ---------------------------------------------------

    if diagnosis == "Unclear Symptoms":

        if "pain" in symptoms:
            diagnosis = "General Fatigue"
            doctor = "General Physician"

        elif "head" in symptoms:
            diagnosis = "Headache"
            doctor = "Neurologist"

    # ---------------------------------------------------
    # SAVE HISTORY
    # ---------------------------------------------------

    conn.execute(
        '''
        INSERT INTO history
        (email, symptoms, diagnosis, advice, specialist)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (
            current_user_email,
            symptoms,
            diagnosis,
            advice,
            doctor
        )
    )

    conn.commit()

    conn.close()

    # ---------------------------------------------------
    # RETURN RESPONSE
    # ---------------------------------------------------

    return jsonify({

        "status": "success",

        "diagnosis": diagnosis,

        "advice": advice,

        "recommended_specialist": doctor,

        "urgency": urgency,

        "top_predictions": top_predictions
    })

# --- ROUTE: SIGNUP ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (email, password, usage_count) VALUES (?, ?, ?)', (email, hashed_password, 0))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Account created successfully!"})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"status": "error", "message": "Email already exists."})
    except Exception as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)})


# --- ROUTE: LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user'] = email
        return jsonify({"status": "success", "message": "Login Successful"})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"})

# --- ROUTE: UPGRADE ---
@app.route('/upgrade', methods=['POST'])
def upgrade():
    if 'user' not in session: return jsonify({"status": "error"})
    
    conn = get_db_connection()
    conn.execute('UPDATE users SET usage_count = -100 WHERE email = ?', (session['user'],))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Premium Activated!"})

# --- ROUTE: DOWNLOAD PDF REPORT ---
@app.route('/download_report')
def download_report():
    if 'user' not in session:
        return redirect(url_for('home'))
        
    email = session['user']
    conn = get_db_connection()
    
    # Get the most recent symptom check for this user
    latest_record = conn.execute('SELECT * FROM history WHERE email = ? ORDER BY timestamp DESC LIMIT 1', (email,)).fetchone()
    conn.close()

    if not latest_record:
        return "No history found to generate a report.", 404

    # Generate the PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(2, 132, 199) # HealthCompass Sky Blue
    pdf.cell(200, 15, txt="HealthCompass AI Report", ln=True, align='C')
    pdf.ln(10)

    # Patient Info
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"Patient ID: {email.split('@')[0]}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {latest_record['timestamp']}", ln=True)
    pdf.line(10, 50, 200, 50)
    pdf.ln(10)

    # Symptoms
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Symptoms Reported:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, txt=latest_record['symptoms'].capitalize())
    pdf.ln(5)

    # Diagnosis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="AI Diagnosis:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, txt=latest_record['diagnosis'])
    pdf.ln(5)

    # Advice
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Medical Advice:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, txt=latest_record['advice'])
    pdf.ln(5)

    # Specialist
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Recommended Specialist:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=latest_record['specialist'], ln=True)

    # Footer Disclaimer
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 8, txt="Disclaimer: This report is generated by an AI model and does not constitute professional medical advice. Please consult a qualified healthcare provider.")

    # Save PDF to memory and send it to the browser
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='HealthCompass_Report.pdf'
    )

# --- ROUTE: LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)