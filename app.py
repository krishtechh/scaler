import torch
from transformers import BertTokenizer, BertForSequenceClassification

# load model
model_path = "models/bert_model"

tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)

model.eval()

# label mapping (IMPORTANT — match your training)
labels = [
    "benign",
    "constraint_bypass",
    "instruction_override",
    "obfuscated",
    "prompt_extraction",
    "role_reassignment"
]

def predict(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    confidence, pred_class = torch.max(probs, dim=1)

    return labels[pred_class.item()], confidence.item()

# interactive loop
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