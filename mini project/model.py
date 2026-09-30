from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
import pandas as pd

df = pd.read_csv("bug_dataset_clean_balanced1.csv")


X = df["text"]
y = df["Priority"]

X_train,X_test,y_train,y_test = train_test_split(
    X,y,test_size=0.2,stratify=y,random_state=42
)
pipeline = Pipeline([
    ("tfidf",TfidfVectorizer(

        ngram_range=(1,2),
        max_features=20000,
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,

    
    )),
    ("model",LinearSVC(
        C=1.5,
        class_weight="balanced",
        max_iter=10000))
])

pipeline.fit(X_train,y_train)

y_pred = pipeline.predict(X_test)



print("Accuracy:",accuracy_score(y_test,y_pred))