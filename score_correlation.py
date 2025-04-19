import re
import pandas as pd
from html import unescape
from difflib import get_close_matches
from rapidfuzz import process, fuzz


def normalize(text):
    return unescape(text).replace("&#xA;", " ").replace("\n", " ").replace("\r", "").strip().lower()


# Load GPT detection results
gpt_df = pd.read_csv("data/2023-output.csv")
gpt_df["Post Text"] = gpt_df["Post Text"].astype(str).str.strip()
gpt_df.rename(columns={"Post Text": "Text", "Score": "GPT_Score"}, inplace=True)
gpt_df["Text"] = gpt_df["Text"].apply(normalize)
gpt_df["GPT_Score"] = gpt_df["GPT_Score"] / 100
print(gpt_df["GPT_Score"].describe())

# Step 1: Extract helpful posts (Score ≥ 3) from the XML lines
helpful_texts = []

with open("data/sample_2023_1000.txt", "r") as f:
    for line in f:
        score_match = re.search(r'Score="(\d+)"', line)
        text_match = re.search(r'Text="(.*?)"', line)
        if score_match and text_match:
            score = int(score_match.group(1))
            text = normalize(text_match.group(1))
            # text = unescape(text_match.group(1)).strip()  # decode &quot;, etc.
            if score > 2:
            # if score >= 3:
                helpful_texts.append(text)

# print(f"Found {len(helpful_texts)} helpful posts (Score ≥ 3)")
print(f"Found {len(helpful_texts)} helpful posts with Score > 2")


# Step 2: Match helpful posts to GPT results
gpt_texts_list = gpt_df["Text"].tolist()  # double check if text of gpt results is normalized!

# fuzzy_matches = []
# threshold = 0.2  # you can try 0.85–0.95 to adjust strictness
threshold_score = 80  # RapidFuzz score (0–100 scale)

# matched_helpful_texts = []
# for helpful in helpful_texts:
#     close = get_close_matches(helpful, gpt_texts_list, n=1, cutoff=threshold)
#     if close:
#         fuzzy_matches.append(close[0])
#         matched_helpful_texts.append(helpful) # track the original helpful text
matched_indices = []
matched_helpful_texts = []

for helpful in helpful_texts:
    result = process.extractOne(helpful, gpt_texts_list, scorer=fuzz.token_sort_ratio)
    if result and result[1] >= threshold_score:
        matched_index = gpt_texts_list.index(result[0])
        matched_indices.append(matched_index)
        matched_helpful_texts.append(helpful)
# for helpful in helpful_texts:
#     result = process.extractOne(
#         helpful, gpt_texts_list, scorer=fuzz.token_sort_ratio
#     )
#     if result and result[1] >= 80:
#         matched_index = gpt_texts_list.index(result[0])
#         matched_indices.append(matched_index)
#         matched_helpful_texts.append(helpful)


# print(f"\nFuzzy matched {len(fuzzy_matches)} of {len(helpful_texts)} helpful posts (threshold = {threshold})")

# Identify helpful posts that didn't match
unmatched_texts = [text for text in helpful_texts if text not in matched_helpful_texts]

print(f"\n❌ {len(unmatched_texts)} helpful posts did NOT match any GPT-scored entry:")
for t in unmatched_texts:
    # print("-", t[:120])  # Print first 120 chars to preview
    print("-\n" + t + "\n" + "-"*40)

# Step 3: Get matching GPT scores
matched_df = gpt_df.iloc[matched_indices].copy()

# matched_df = gpt_df[gpt_df["Text"].isin(fuzzy_matches)]
# matched_df = matched_df.copy()
matched_df["Likely_GPT"] = matched_df["GPT_Score"] >= 0.8
print(matched_df.sort_values("GPT_Score", ascending=False)[["GPT_Score", "Text"]].head(10))

# print(matched_df.sort_values("GPT_Score", ascending=False)[["Text", "GPT_Score"]].head()) 


# Step 4: Summary
total_matched = len(matched_df)
likely_gpt = matched_df["Likely_GPT"].sum()

print(f"{likely_gpt} of {total_matched} helpful posts are likely GPT-generated ({likely_gpt / total_matched:.2%})")


# Visualize the result
from tabulate import tabulate
summary = [
    ["Total Posts Analyzed", 1000],
    ["Helpful Posts (Score > 2)", len(helpful_texts)],
    ["Matched to GPT Results", total_matched],
    ["Likely GPT-Generated (≥ 0.8)", likely_gpt],
    ["Unmatched Helpful Posts", len(unmatched_texts)]
]

print("\n📊 Summary Table:")
print(tabulate(summary, headers=["Metric", "Value"], tablefmt="github"))

import matplotlib.pyplot as plt

labels = ['Helpful Posts', 'Matched', 'Likely GPT']
values = [len(helpful_texts), total_matched, likely_gpt]

plt.bar(labels, values)
plt.title('2024 Helpful Posts and GPT Presence')
plt.ylabel('Post Count')
plt.ylim(0, max(values) + 5)
plt.show()
