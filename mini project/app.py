from flask import Flask, render_template, request, jsonify
import joblib
import re
import numpy as np
import requests   # for Ollama

app = Flask(__name__)

# ================= LOAD MODEL =================
model = joblib.load("bug_severity_model.pkl")
tfidf = joblib.load("tfidf_vectorizer.pkl")

# ================= CLEAN INPUT =================
def clean_input(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ================= RULE ENGINE (SEVERITY FIX) =================
def rule_based_fix(text, severity):

    ui_keywords = ["ui","alignment","spacing","color","font","layout","button"]
    perf_keywords = ["slow","lag","performance","memory","cpu","crash","delay"]

    if severity == "HIGH":
        return severity

    if any(w in text for w in perf_keywords):
        return "MEDIUM"

    if severity == "MEDIUM" and any(w in text for w in ui_keywords):
        return "LOW"

    return severity

# ================= RULE-BASED SOLUTION =================
def get_rule_solution(text):
    text = text.lower()

    rules = [
        {
            "type": "Crash Bug",
            "keywords": ["crash", "exception", "fatal", "error", "fail", "not working", "stopped"],
            "root": "Unhandled exception, memory issue, or environment mismatch",
            "fix": [
                "Analyze logs to identify exact failure point",
                "Handle null/undefined values before access",
                "Use try-catch with proper logging",
                "Check memory usage for large data processing",
                "Verify production vs local environment configuration",
                "Add graceful fallback to prevent crash"
            ]
        },
        {
            "type": "Performance Issue",
            "keywords": ["slow", "lag", "delay", "timeout"],
            "root": "Inefficient code or heavy operations",
            "fix": [
                "Optimize loops",
                "Reduce API calls",
                "Use caching",
                "Optimize database queries"
            ]
        },
        {
            "type": "UI Bug",
            "keywords": ["ui", "alignment", "layout", "button"],
            "root": "CSS or responsiveness issue",
            "fix": [
                "Fix CSS styles",
                "Use Flexbox/Grid",
                "Improve responsiveness"
            ]
        },
        {
            "type": "Authentication Bug",
            "keywords": ["login", "session", "token"],
            "root": "Authentication/session issue",
            "fix": [
                "Validate tokens",
                "Check session expiry",
                "Fix login logic"
            ]
        }
    ]

    results = []

    for rule in rules:
        if any(word in text for word in rule["keywords"]):
            results.append(rule)

    return results if results else None

# ================= OLLAMA AI SOLUTION =================
def get_ai_solution(text):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": f"""
Bug: {text}

Act like a senior software engineer.

Give:
1. Root Cause
2. Solution
3. Steps to fix

Keep it short and practical.
""",
                "stream": False
            }
        )

        return response.json().get("response", "⚠️ No response from AI")

    except Exception as e:
        return f"⚠️ AI not working: {str(e)}"

# ================= HYBRID SOLUTION =================
def get_solution(text, confidence):

    rule = get_rule_solution(text)
    rule_count = len(rule) if rule else 0

    # DEBUG (optional)
    print("Confidence:", confidence)
    print("Rule Found:", bool(rule))
    print("Rule Count:", rule_count)

    # ✅ RULE ONLY
    if rule and rule_count==1 and confidence > 80:
        return {
            "source": "rule",
            "data": rule
        }

    # ✅ HYBRID
    elif rule and rule_count>1 :
        ai = get_ai_solution(text)
        return {
            "source": "hybrid",
            "rule": rule,
            "ai": ai
        }
    elif rule and confidence <= 80:
        ai = get_ai_solution(text)
        return {
            "source": "hybrid",
            "rule": rule,
            "ai": ai
        }

    # ✅ AI ONLY
    else:
        ai = get_ai_solution(text)
        return {
            "source": "ai",
            "data": ai
        }

# ================= PREDICTION =================
def predict_bug(text):

    text_clean = clean_input(text)
    X = tfidf.transform([text_clean])

    scores = model.decision_function(X)[0]
    classes = model.classes_

    sorted_idx = np.argsort(scores)
    top1 = sorted_idx[-1]
    top2 = sorted_idx[-2]

    severity = classes[top1]

    gap = scores[top1] - scores[top2]
    confidence = round((1 / (1 + np.exp(-gap))) * 100, 2)

    severity = rule_based_fix(text_clean, severity)

    priority_map = {
        "HIGH": "P1",
        "MEDIUM": "P2",
        "LOW": "P3"
    }

    priority = priority_map.get(severity, "P4")

    return severity, priority, confidence

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()
    desc = data["description"]

    severity, priority, confidence = predict_bug(desc)

    # ALERT SYSTEM
    if priority == "P1":
        alert = "🚨 CRITICAL ALERT: Immediate action required!"
    elif priority == "P2":
        alert = "⚠️ High Priority: Fix soon"
    elif priority == "P3":
        alert = "ℹ️ Medium Priority: Can be scheduled"
    else:
        alert = "✅ Low Priority: Minor issue"

    # GET SOLUTION
    solution = get_solution(desc, confidence)

    return jsonify({
        "severity": severity,
        "priority": priority,
        "confidence": confidence,
        "alert": alert,
        "solution": solution
    })

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)