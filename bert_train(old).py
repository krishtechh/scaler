import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, trainer, TrainingArguments
from datasets import Dataset 

df=pd.read_csv("data/prompts.csv")

#encoding attack type
label_encoder=LabelEncoder()
df["labels"]=label_encoder.fit_transform(df['attack_type'])
print("Label Mapping:")
for i, label in enumerate(label_encoder.classes_):
    print(f"{label} → {i}")

# Train-test split
# -----------------------------
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["labels"]
)

#converting to dataset
train_dataset = Dataset.from_pandas(train_df[["prompt", "labels"]])
test_dataset = Dataset.from_pandas(test_df[["prompt", "labels"]])

#load tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def tokenize(example):
    return tokenizer(example["prompt"], padding="max_length", truncation=True)

train_dataset = train_dataset.map(tokenize, batched=True)
test_dataset = test_dataset.map(tokenize, batched=True)

train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
test_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

#load model
num_labels = len(label_encoder.classes_)

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=num_labels
)

#training settings
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=8,
    evaluation_strategy="epoch",
    logging_dir="./logs",
    save_strategy="epoch",
)

#trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

#training
trainer.train()

#saving model
model.save_pretrained("models/bert_model")
tokenizer.save_pretrained("models/bert_model")

print("BERT training complete!")
