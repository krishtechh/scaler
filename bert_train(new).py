from transformers import BertTokenizer, BertForSequenceClassification
import torch

#loading trained model
model = BertForSequenceClassification.from_pretrained("models/bert_model")
tokenizer = BertTokenizer.from_pretrained("models/bert_model")

model.eval()

labels = [
    "benign",
    "constraint_bypass",
    "instruction_override",
    "obfuscated",
    "prompt_extraction",
    "role_reassignment"
]

print("BERT Prompt Injection Detector Ready !")

while True:
    text = input("\nEnter prompt: ")

    if text.lower() == "exit":
        break

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    pred = torch.argmax(probs).item()

    confidence = probs[0][pred].item()

    print(f"\nPrediction: {labels[pred]}")
    print(f"Confidence: {confidence:.2f}")