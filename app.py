import joblib

# load pre-trained sklearn model and vectorizer
# No heavy training or huggingface download required!
print("Loading lightning-fast local sklearn baseline...")
vectorizer = joblib.load("models/vectorizer.pkl")
model = joblib.load("models/model.pkl")

def predict(prompt):
    # Vectorize the text
    X = vectorizer.transform([prompt])
    
    # Get probability of class 1 (malicious)
    prob = model.predict_proba(X)[0][1]
    
    # If prob >= 0.5 we consider it malicious
    if prob >= 0.5:
        label = "malicious_attack"
    else:
        label = "benign"
        
    # Standardize confidence to be max of the two probabilities for display
    confidence = max(prob, 1.0 - prob)
    return label, confidence

# interactive loop
print("Ready!")
while True:
    text = input("\n Enter prompt (type 'exit' to quit): ")

    if text.lower() == "exit":
        break

    label, conf = predict(text)

    print("\n Result:")
    
    if label == "benign":
        print(" This is a SAFE prompt")
        print(" Prompt allowed to go to LLM")
    else:
        print(f" Malicious prompt detected: {label}")
        print(" prompt BLOCKED for safety")

    print(f" Confidence: {conf:.2f}")