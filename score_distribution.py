import re
from collections import Counter
import matplotlib.pyplot as plt

scores = []

with open("data/sample_2023_1000.txt", "r") as file:
    for line in file:
        match = re.search(r'Score="(\d+)"', line)
        if match:
            scores.append(int(match.group(1)))

# Print basic stats
print(f"Total posts: {len(scores)}")
print(f"Max score: {max(scores)}")
print(f"Min score: {min(scores)}")
print(f"Average score: {sum(scores)/len(scores):.2f}")

# Show score distribution
score_counts = Counter(scores)
plt.bar(score_counts.keys(), score_counts.values())
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.title("Score Distribution (Sample 2023)")
plt.show()