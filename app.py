import joblib

model = joblib.load("models/model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

def predict_prompt(prompt):
    vector = vectorizer.transform([prompt])

    prediction = model.predict(vector)[0]
    probability = model.predict_proba(vector)[0][prediction]

    label = "This is a Malicious" if prediction == 1 else "This is a Benign"

    return f"{label} prompt! (confidence: {probability:.2f})"

while True:
    text = input("Enter the prompt: \n")
    print(predict_prompt(text))