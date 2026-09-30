import joblib
import re

# Load the saved model and vectorizer
model = joblib.load("bug_severity_model.pkl")
tfidf = joblib.load("tfidf_vectorizer.pkl")
def rule_based_fix(text, severity):
    
    text = text.lower()

    ui_keywords = ["ui", "alignment", "spacing", "color", "font", "layout","color","font","button","design"]
    perf_keywords= ["slow", "lag", "performance", "memory", "cpu", "crash","freezes","timeout","delay"]
    session_keywords = ["session", "timeout", "expire", "logout", "cookie", "authentication","login","token"]
    if severity=="HIGH":
        return severity

    if any(word in text for word in perf_keywords):
        return "MEDIUM"
    if any(word in text for word in session_keywords):
        return "MEDIUM"

    # if UI-related → downgrade severity
    if severity=="MEDIUM" and any(word in text for word in ui_keywords):
        print("Rule-based fix applied: Downgrading severity from MEDIUM to LOW due to UI-related keywords.")
        return "LOW"

    return severity
def clean_input(text):
    text = str(text).lower()
    text = re.sub(r"http\S+","",text)
    text = re.sub(r"\d+","",text)
    text = re.sub(r"[^a-zA-Z\s]"," ",text)
    text = re.sub(r"\s+"," ",text).strip()
    return text

import numpy as np

def predict_bug(text):

    text = clean_input(text)
    text_tfidf = tfidf.transform([text])

    scores = model.decision_function(text_tfidf)[0]
    classes = model.classes_

    # Sort scores
    sorted_idx = np.argsort(scores)

    top1_idx = sorted_idx[-1]
    top2_idx = sorted_idx[-2]

    top1_label = classes[top1_idx]
    top1_score = scores[top1_idx]
    top2_score = scores[top2_idx]

    # STABLE CONFIDENCE (SIGMOID ON GAP)
    gap = top1_score - top2_score
    confidence = 1 / (1 + np.exp(-gap))
    confidence = round(confidence * 100, 2)

    # Apply rule
    severity = rule_based_fix(text, top1_label)

    # Priority mapping
    if severity == "HIGH":
        priority = "P1"
    elif severity == "MEDIUM":
        priority = "P2"
    elif severity == "LOW":
        priority = "P3"
    else:
        priority = "P4"

    return severity, priority, confidence
def alert_system(priority):
    
    if priority == "P1":
        print("🚨 CRITICAL ALERT: Immediate action required!")
    
    elif priority == "P2":
        print("⚠️ High Priority: Fix soon")
    
    elif priority == "P3":
        print("ℹ️ Medium Priority: Can be scheduled")
    
    else:
        print("✅ Low Priority: Minor issue")

while True:
    
    user_input = input("\nEnter bug description (or 'exit'): ")
    
    if user_input.lower() == "exit":
        break

    severity, priority, confidence = predict_bug(user_input)

    print("Predicted Severity:", severity)
    print("Predicted Priority:", priority)
    print("Confidence:", confidence,"%")

    alert_system(priority) 

