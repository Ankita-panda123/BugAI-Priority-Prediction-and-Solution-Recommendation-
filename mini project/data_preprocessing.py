import pandas as pd
import re

df = pd.read_csv("bug_dataset_clean_balanced.csv")


print(df['Severity Label'].value_counts())
# ✅ CLEAN TEXT (SIMPLE + SAFE)
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+","",text)
    text = re.sub(r"\d+","",text)
    text = re.sub(r"[^a-zA-Z0-9\s]"," ",text)
    text = re.sub(r"\s+"," ",text)
    return text.strip()

df["text"] = df["text"].apply(clean_text)

# ✅ ADD CROSS VALIDATION HERE
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        stop_words="english",
        ngram_range=(1,2),
        max_features=50000,
        min_df=2,
        max_df=0.9,
        sublinear_tf=True

    )),
    ("model", LinearSVC(C=2.0,class_weight={"HIGH": 1, "LOW": 1,"VERY_LOW": 1},max_iter=15000))
])

scores = cross_val_score(
    pipeline,
    df["text"],
    df["Severity Label"],
    cv=5,
    scoring="accuracy"
)

print("Cross Validation Scores:", scores)
print("Average Accuracy:", scores.mean())
df['text']=df["Project"].fillna("")+" "+df["Short Description"].fillna("")

X = df["text"]
y = df["Severity Label"]

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# # ✅ KEEP TF-IDF SIMPLE (this is key)
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(

    ngram_range=(1,2),
    max_features=35000,
    min_df=2
)

X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)


model = LinearSVC(C=1.5,class_weight="balanced",max_iter=15000)

model.fit(X_train_tfidf, y_train)

# # ✅ PREDICT
from sklearn.metrics import accuracy_score, classification_report

y_pred = model.predict(X_test_tfidf)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

from sklearn.metrics import confusion_matrix
import pandas as pd

cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
cm_df = pd.DataFrame(cm, index=model.classes_, columns=model.classes_)
print(cm_df)



# # ✅ Top-2 Accuracy
import numpy as np

scores = model.decision_function(X_test_tfidf)

top2 = np.argsort(scores, axis=1)[:, -2:]

labels = model.classes_

correct = 0

for i, true_label in enumerate(y_test):
    if true_label in labels[top2[i]]:
        correct += 1

print("Top-2 Accuracy:", correct / len(y_test))


import joblib
joblib.dump(model, "bug_severity_model.pkl")
joblib.dump(tfidf, "tfidf_vectorizer.pkl")
print("Model and TF-IDF saved successfully!")