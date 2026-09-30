import pandas as pd
import re
from sklearn.utils import resample

# ---------------- LOAD DATA ----------------
df = pd.read_csv("balanced.csv")
print("Original Shape:", df.shape)

# ---------------- REMOVE DUPLICATES ----------------
df = df.drop_duplicates(subset=["Short Description"])

# ---------------- CLEAN TEXT ----------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

df["Project"] = df["Project"].astype(str).apply(clean_text)
df["Short Description"] = df["Short Description"].astype(str).apply(clean_text)

# ---------------- MERGE TEXT ----------------
df["text"] = df["Project"] + " " + df["Short Description"]

# ---------------- REMOVE NOISY DATA ----------------
df = df[df["text"].str.split().str.len() > 4]
df = df[~df["text"].str.contains("test|dummy|sample", case=False)]

# ---------------- MAP SEVERITY ----------------
def map_severity(sev):
    sev = str(sev).lower()

    if sev in ["blocker", "critical"]:
        return "HIGH"
    elif sev == "major":
        return "MEDIUM"
    elif sev in ["minor", "normal"]:
        return "LOW"
    else:
        return "VERY_LOW"

df["Severity Label"] = df["Severity Label"].apply(map_severity)

print("\nAfter Mapping:")
print(df["Severity Label"].value_counts())

# ---------------- DEFINE KEYWORDS ----------------
ui_keywords = ["ui", "alignment", "color", "font", "layout", "button", "design", "spacing"]
perf_keywords = ["slow", "delay", "freeze", "lag", "timeout", "performance"]

def has_keywords(text, keywords):
    return any(word in text for word in keywords)

# ---------------- 🔥 SMART RELABELING ----------------
def fix_low_class(row):
    text = row["text"]

    # LOW but actually performance → move to MEDIUM
    if row["Severity Label"] == "LOW":
        if has_keywords(text, perf_keywords):
            return "MEDIUM"

    return row["Severity Label"]

df["Severity Label"] = df.apply(fix_low_class, axis=1)

# ---------------- REMOVE TRUE OVERLAP ----------------
df = df[~df["text"].apply(
    lambda x: has_keywords(x, ui_keywords) and has_keywords(x, perf_keywords)
)]

# ---------------- CLEAN LOW CLASS ----------------
df = df[~(
    (df["Severity Label"] == "LOW") &
    (~df["text"].str.contains("ui|alignment|color|font|layout|button|design", case=False))
)]

# ---------------- CLEAN MEDIUM CLASS ----------------
df = df[~(
    (df["Severity Label"] == "MEDIUM") &
    (~df["text"].str.contains("slow|delay|freeze|lag|timeout|performance", case=False))
)]

# ---------------- FINAL TEXT FILTER ----------------
df = df[df["text"].str.split().str.len() > 5]

# ---------------- SPLIT CLASSES ----------------
HIGH = df[df['Severity Label'] == 'HIGH']
MEDIUM = df[df['Severity Label'] == 'MEDIUM']
LOW = df[df['Severity Label'] == 'LOW']
VERY_LOW = df[df['Severity Label'] == 'VERY_LOW']

# ---------------- BALANCING ----------------
target = 6500

HIGH_sample = resample(HIGH, replace=True, n_samples=target, random_state=42)
MEDIUM_sample = resample(MEDIUM, replace=True, n_samples=target, random_state=42)
LOW_sample = resample(LOW, replace=True, n_samples=target, random_state=42)
VERY_LOW_sample = resample(VERY_LOW, replace=True, n_samples=4000, random_state=42)

# ---------------- COMBINE ----------------
df_balanced = pd.concat([
    HIGH_sample,
    MEDIUM_sample,
    LOW_sample,
    VERY_LOW_sample
])

# ---------------- SHUFFLE ----------------
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print("\nFinal Distribution:")
print(df_balanced["Severity Label"].value_counts())

print("\nFinal Shape:", df_balanced.shape)

# ---------------- SAVE ----------------
df_balanced.to_csv("bug_dataset_clean_balanced.csv", index=False)

print("\n✅ Dataset saved successfully!")