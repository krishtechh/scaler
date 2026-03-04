import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.model_selection import cross_val_score,StratifiedKFold
from sklearn.metrics import roc_auc_score
import numpy as np
import joblib

#loading dataset
df=pd.read_csv("data/prompts.csv")

#features and labels
X=df['prompt']
Y=df['label']

#5 fold cross validation
print("\nRunning 5 fold cross validation")
vectorizer_cv = TfidfVectorizer(ngram_range=(1, 2))
X_tfidf_full = vectorizer_cv.fit_transform(X)

model_cv = LogisticRegression(max_iter=1000, class_weight="balanced")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_scores=cross_val_score(
    model_cv,
    vectorizer_cv.fit_transform(X),
    Y,
    cv=cv,
    scoring="f1_macro"
)

#train test split
X_train,X_test,Y_train,Y_test=train_test_split(
    X,Y,test_size=0.2,random_state=42,stratify=Y
)

#tfidf vectorization 
vectorizer=TfidfVectorizer(ngram_range=(1,2))
X_train_tfidf=vectorizer.fit_transform(X_train)
X_test_tfidf=vectorizer.transform(X_test)

#training classifier
model=LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train_tfidf,Y_train)

# Predictions
Y_pred = model.predict(X_test_tfidf)

# ROC-AUC
y_prob = model.predict_proba(X_test_tfidf)[:, 1]
roc_auc = roc_auc_score(Y_test, y_prob)
print("\nROC-AUC Score:", roc_auc)

# Evaluation
print("Confusion Matrix:")
print(confusion_matrix(Y_test, Y_pred))

print("\nClassification Report:")
print(classification_report(Y_test, Y_pred, zero_division=0))

joblib.dump(model, "models/model.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")
