import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report
)
import joblib
import os

# ---------------------------------------------------
# URGENCY / SEVERITY LEVELS
# ---------------------------------------------------

URGENCY_LEVELS = {

    'Common_Cold': 'Low',
    'Allergic_Rhinitis': 'Low',

    'Influenza': 'Moderate',
    'COVID_19': 'Moderate',
    'Food_Poisoning': 'Moderate',
    'Migraine': 'Moderate',
    'Typhoid': 'Moderate',
    'Gastroenteritis': 'Moderate',
    'Hypertension': 'Moderate',
    'Diabetes': 'Moderate',

    'Pneumonia': 'High',
    'Dengue': 'High',
    'Malaria': 'High',

    'Asthma': 'Emergency',

    'Anxiety_Disorder': 'Low'
}

# ---------------------------------------------------
# LOAD & PREPROCESS DATA
# ---------------------------------------------------

def load_and_preprocess(filename):

    if not os.path.exists(filename):
        print(f"Error: {filename} not found!")
        return None, None

    df = pd.read_csv(filename)

    # Last column = target disease
    y = df.iloc[:, -1]

    # All remaining columns = symptoms
    symptom_columns = df.columns[:-1]

    X_text = []

    for _, row in df.iterrows():

        active_symptoms = []

        for col in symptom_columns:

            if row[col] == 1:
                active_symptoms.append(col.replace('_', ' '))

        X_text.append(" ".join(active_symptoms))

    return X_text, y


# ---------------------------------------------------
# PREDICTION FUNCTION
# ---------------------------------------------------

def predict_disease(symptoms_text):

    probs = model.predict_proba([symptoms_text])[0]

    disease_names = model.classes_

    disease_probabilities = list(zip(disease_names, probs))

    # Sort by probability descending
    disease_probabilities.sort(
        key=lambda x: x[1],
        reverse=True
    )

    top_3 = disease_probabilities[:3]

    print("\n==============================")
    print("TOP POSSIBLE CONDITIONS")
    print("==============================\n")

    top_3_total = sum(prob for _, prob in top_3)

    for disease, probability in top_3:

        normalized_probability = (
            probability / top_3_total
        ) * 100

        urgency = URGENCY_LEVELS.get(disease, "Unknown")

        print(f"Disease       : {disease}")
        print(f"Probability   : {normalized_probability:.2f}%")
        print(f"Urgency Level : {urgency}")

        # Basic recommendation system
        if urgency == "Low":
            recommendation = "Monitor symptoms and rest."

        elif urgency == "Moderate":
            recommendation = "Consult a doctor if symptoms worsen."

        elif urgency == "High":
            recommendation = "Medical consultation recommended soon."

        elif urgency == "Emergency":
            recommendation = "Seek immediate medical attention."

        else:
            recommendation = "No recommendation available."

        print(f"Recommendation: {recommendation}")
        print("-" * 35)


# ---------------------------------------------------
# MAIN TRAINING
# ---------------------------------------------------

print("Loading training data...")

X_train, y_train = load_and_preprocess("training.csv")

if X_train is not None:

    # ---------------------------------------------------
    # AI PIPELINE
    # ---------------------------------------------------

    model = make_pipeline(

        TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english'
        ),

        RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=3,
            random_state=42,
            class_weight='balanced',
            n_jobs=-1
        )
    )

    # ---------------------------------------------------
    # TRAIN MODEL
    # ---------------------------------------------------

    print("Training model...")
    model.fit(X_train, y_train)

    # ---------------------------------------------------
    # SAVE MODEL
    # ---------------------------------------------------

    joblib.dump(model, "health_model.pkl")

    print("\n✅ Model saved successfully as 'health_model.pkl'!")

    # ---------------------------------------------------
    # LOAD TEST DATA
    # ---------------------------------------------------

    print("\nLoading testing data...")

    X_test, y_test = load_and_preprocess("testing.csv")

    if X_test is not None:

        # ---------------------------------------------------
        # EVALUATION
        # ---------------------------------------------------

        print("Evaluating model...")

        pred = model.predict(X_test)

        acc = accuracy_score(y_test, pred)

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test,
            pred,
            average="weighted",
            zero_division=0
        )

        print("\n========== RESULTS ==========")

        print(f"Accuracy  : {acc:.4f}")
        print(f"Precision : {precision:.4f}")
        print(f"Recall    : {recall:.4f}")
        print(f"F1 Score  : {f1:.4f}")

        print("=" * 30)

        # ---------------------------------------------------
        # CLASSIFICATION REPORT
        # ---------------------------------------------------

        print("\nCLASSIFICATION REPORT:\n")

        print(classification_report(
            y_test,
            pred,
            zero_division=0
        ))

        # ---------------------------------------------------
        # SAMPLE USER PREDICTION
        # ---------------------------------------------------

        print("\n========== SAMPLE AI PREDICTION ==========")

        user_symptoms = "fever cough headache fatigue"

        predict_disease(user_symptoms)

        print("\n==========================================")