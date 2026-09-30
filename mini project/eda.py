import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# LOAD DATA
raw = pd.read_csv("balanced.csv")  # raw dataset
clean = pd.read_csv("bug_dataset_clean_balanced.csv")  # cleaned dataset

# ---------------- 📊 FIGURE 1: RAW DISTRIBUTION ----------------
plt.figure()
raw['Severity Label'].value_counts().plot(kind='bar')
plt.title("Raw Dataset Class Distribution")
plt.xlabel("Severity")
plt.ylabel("Count")
plt.savefig("fig1_raw_distribution.png")
plt.close()

# ---------------- 📊 FIGURE 2: CLEANED DISTRIBUTION ----------------
plt.figure()
clean['Severity Label'].value_counts().plot(kind='bar')
plt.title("Cleaned Dataset Distribution")
plt.xlabel("Severity")
plt.ylabel("Count")
plt.savefig("fig2_clean_distribution.png")
plt.close()

# ---------------- 📊 FIGURE 3: TEXT LENGTH ----------------
clean['text_length'] = clean['text'].apply(lambda x: len(str(x).split()))

plt.figure()
plt.hist(clean['text_length'], bins=30)
plt.title("Text Length Distribution")
plt.xlabel("Number of Words")
plt.ylabel("Frequency")
plt.savefig("fig3_text_length.png")
plt.close()

# ---------------- 📊 FIGURE 4: WORDCLOUD ----------------
text = " ".join(clean['text'].astype(str))

wc = WordCloud(width=800, height=400, background_color='white').generate(text)

plt.figure()
plt.imshow(wc)
plt.axis("off")
plt.title("WordCloud of Bug Descriptions")
plt.savefig("fig4_wordcloud.png")
plt.close()

# ---------------- 📊 FIGURE 5: CLASS COMPARISON ----------------
raw_counts = raw['Severity Label'].value_counts()
clean_counts = clean['Severity Label'].value_counts()

df_compare = pd.DataFrame({
    "Raw": raw_counts,
    "Cleaned": clean_counts
}).fillna(0)

df_compare.plot(kind='bar')
plt.title("Raw vs Cleaned Dataset Comparison")
plt.xlabel("Severity")
plt.ylabel("Count")
plt.savefig("fig5_comparison.png")
plt.close()

print("✅ All figures generated successfully!")