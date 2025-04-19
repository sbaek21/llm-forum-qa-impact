import re

input_file = "data/sample_2024_1000.txt"
helpful_lines = []
helpful_post_ids = []

with open(input_file, "r") as f:
    for line in f:
        score_match = re.search(r'Score="(\d+)"', line)
        postid_match = re.search(r'PostId="(\d+)"', line)
        if score_match and postid_match:
            score = int(score_match.group(1))
            if score > 2:
            # if score >= 3:
                helpful_lines.append(line.strip())
                helpful_post_ids.append(postid_match.group(1))

# print(f"Found {len(helpful_post_ids)} helpful posts with Score ≥ 3")
print(f"Found {len(helpful_post_ids)} helpful posts with Score > 2")
