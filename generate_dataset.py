import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

NUM_ROWS = 10000
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ---------------------------------------------------
# SYMPTOMS
# ---------------------------------------------------

SYMPTOMS = [
    'fever',
    'high_fever',
    'cough',
    'dry_cough',
    'fatigue',
    'headache',
    'nausea',
    'vomiting',
    'diarrhea',
    'shortness_of_breath',
    'chest_pain',
    'body_ache',
    'joint_pain',
    'loss_of_smell',
    'loss_of_taste',
    'sore_throat',
    'runny_nose',
    'sneezing',
    'abdominal_pain',
    'dizziness',
    'sweating',
    'chills',
    'blurred_vision',
    'frequent_urination',
    'increased_thirst',
    'weight_loss',
    'anxiety',
    'rapid_heartbeat',
    'wheezing',
    'skin_rash'
]

# ---------------------------------------------------
# DISEASE DEFINITIONS
# Probability values:
# 0.0 -> symptom absent
# 1.0 -> symptom almost always present
# ---------------------------------------------------

DISEASES = {
    'Influenza': {
        'fever': 0.85,
        'cough': 0.75,
        'fatigue': 0.80,
        'body_ache': 0.80,
        'headache': 0.65,
        'chills': 0.60,
        'sore_throat': 0.50
    },

    'Common_Cold': {
        'cough': 0.60,
        'runny_nose': 0.90,
        'sneezing': 0.85,
        'sore_throat': 0.60,
        'fatigue': 0.35
    },

    'COVID_19': {
        'fever': 0.80,
        'dry_cough': 0.80,
        'fatigue': 0.75,
        'loss_of_smell': 0.65,
        'loss_of_taste': 0.60,
        'shortness_of_breath': 0.45,
        'headache': 0.50
    },

    'Migraine': {
        'headache': 0.95,
        'nausea': 0.55,
        'vomiting': 0.35,
        'dizziness': 0.40,
        'fatigue': 0.30
    },

    'Food_Poisoning': {
        'nausea': 0.90,
        'vomiting': 0.85,
        'diarrhea': 0.80,
        'abdominal_pain': 0.75,
        'fever': 0.30
    },

    'Dengue': {
        'high_fever': 0.90,
        'body_ache': 0.85,
        'joint_pain': 0.80,
        'headache': 0.75,
        'skin_rash': 0.45,
        'fatigue': 0.70
    },

    'Malaria': {
        'fever': 0.85,
        'chills': 0.90,
        'sweating': 0.75,
        'headache': 0.55,
        'vomiting': 0.35,
        'fatigue': 0.65
    },

    'Pneumonia': {
        'fever': 0.80,
        'cough': 0.85,
        'shortness_of_breath': 0.75,
        'chest_pain': 0.55,
        'fatigue': 0.65
    },

    'Asthma': {
        'shortness_of_breath': 0.90,
        'wheezing': 0.90,
        'cough': 0.55,
        'chest_pain': 0.30,
        'rapid_heartbeat': 0.30
    },

    'Diabetes': {
        'frequent_urination': 0.90,
        'increased_thirst': 0.85,
        'fatigue': 0.50,
        'weight_loss': 0.45,
        'blurred_vision': 0.35
    },

    'Hypertension': {
        'headache': 0.45,
        'dizziness': 0.40,
        'chest_pain': 0.30,
        'rapid_heartbeat': 0.35,
        'fatigue': 0.25
    },

    'Anxiety_Disorder': {
        'anxiety': 0.95,
        'rapid_heartbeat': 0.70,
        'dizziness': 0.50,
        'fatigue': 0.40,
        'shortness_of_breath': 0.35
    },

    'Allergic_Rhinitis': {
        'runny_nose': 0.90,
        'sneezing': 0.90,
        'cough': 0.25,
        'sore_throat': 0.25
    },

    'Typhoid': {
        'high_fever': 0.85,
        'abdominal_pain': 0.55,
        'fatigue': 0.75,
        'headache': 0.50,
        'diarrhea': 0.40
    },

    'Gastroenteritis': {
        'diarrhea': 0.90,
        'vomiting': 0.75,
        'abdominal_pain': 0.80,
        'fever': 0.30,
        'fatigue': 0.40
    }
}

# ---------------------------------------------------
# DATA GENERATION FUNCTION
# ---------------------------------------------------


def generate_patient(disease_name, symptom_probs):
    patient = {}

    for symptom in SYMPTOMS:

        # default random noise
        patient[symptom] = 0

        # if symptom belongs to disease profile
        if symptom in symptom_probs:
            prob = symptom_probs[symptom]
            patient[symptom] = 1 if random.random() < prob else 0

        # add realistic random noise (helps prevent overfitting)
        else:
            patient[symptom] = 1 if random.random() < 0.03 else 0

    # additional random missing symptom behavior
    # simulates incomplete symptom reporting
    for symptom in random.sample(SYMPTOMS, k=2):
        if random.random() < 0.15:
            patient[symptom] = 0

    patient['disease'] = disease_name

    return patient


# ---------------------------------------------------
# GENERATE DATASET
# ---------------------------------------------------

all_rows = []

disease_names = list(DISEASES.keys())
rows_per_disease = NUM_ROWS // len(disease_names)

for disease in disease_names:

    symptom_profile = DISEASES[disease]

    for _ in range(rows_per_disease):
        row = generate_patient(disease, symptom_profile)
        all_rows.append(row)


# ---------------------------------------------------
# CREATE DATAFRAME
# ---------------------------------------------------

df = pd.DataFrame(all_rows)

# Shuffle dataset

df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

# ---------------------------------------------------
# TRAIN TEST SPLIT
# ---------------------------------------------------

train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    stratify=df['disease'],
    random_state=RANDOM_SEED
)

# ---------------------------------------------------
# SAVE FILES
# ---------------------------------------------------

train_df.to_csv('training.csv', index=False)
test_df.to_csv('testing.csv', index=False)

print('Dataset generated successfully!')
print(f'Training rows: {len(train_df)}')
print(f'Testing rows : {len(test_df)}')