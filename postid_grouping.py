import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches


# Extract the value of a given attribute key from a line
def extract_attribute(line, key):
    start = line.find(f'{key}="')
    if start == -1:
        return None
    start += len(key) + 2
    end = line.find('"', start)
    return line[start:end]

# Load GPT scores from CSV file
def load_gpt_scores_from_csv(gpt_file_path, max_lines):
    df = pd.read_csv(gpt_file_path)
    scores = df["Score"].tolist()[:max_lines]
    return scores


def group_and_sort_comments_with_offset(comment_file_path, gpt_scores, max_lines):
    grouped = {}
    post_times = {}  # New: Track earliest comment time as proxy for post time
    score_index = 0
    line_count = 0
    comments_data = []

    with open(comment_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line_count >= max_lines:
                break
            if '<row' in line:
                post_id = extract_attribute(line, 'PostId')
                comment_id = extract_attribute(line, 'Id')
                text = extract_attribute(line, 'Text')
                score = int(extract_attribute(line, 'Score') or 0)
                creation_date_str = extract_attribute(line, 'CreationDate')
                creation_date = datetime.strptime(creation_date_str, '%Y-%m-%dT%H:%M:%S.%f')

                # Assign GPT score
                gpt_score = gpt_scores[score_index] if score_index < len(gpt_scores) else None
                score_index += 1

                if post_id:
                    # Use the first-seen comment as a proxy for post time
                    if post_id not in post_times:
                        post_times[post_id] = creation_date

                    time_offset_sec = (creation_date - post_times[post_id]).total_seconds()

                    comment = {
                        'PostId': post_id,
                        'CommentId': comment_id,
                        'Score': score,
                        'GPTScore': gpt_score,
                        'CreationDate': creation_date,
                        'TimeOffset': time_offset_sec
                    }
                    comments_data.append(comment)
                line_count += 1

    return comments_data


# Example Usage:
if __name__ == "__main__":
    comment_file_path = 'data/sample_2024_1000.txt'
    gpt_file_path = 'data/2024-output.csv'
    max_lines = 1000 # Number of lines to process

    gpt_scores = load_gpt_scores_from_csv(gpt_file_path, max_lines)

    comments_data = group_and_sort_comments_with_offset(comment_file_path, gpt_scores, max_lines)

    # Plot TimeOffset vs. Score
    offsets = [c['TimeOffset'] for c in comments_data]
    scores = [c['Score'] for c in comments_data]
    colors = ['red' if c['GPTScore'] is not None and c['GPTScore'] >= 0.8 else 'blue' for c in comments_data]
    sizes = [60 if c['GPTScore'] is not None and c['GPTScore'] >= 0.8 else 15 for c in comments_data]
    red_patch = mpatches.Patch(color='red', label='GPT-Generated')
    blue_patch = mpatches.Patch(color='blue', label='Human-Authored')

    plt.figure(figsize=(10, 6))
    plt.scatter(offsets, scores, c=colors, s=sizes, alpha=0.7, edgecolors='k')
    plt.xlabel('Time Offset from First Comment (seconds)')
    plt.ylabel('Comment Upvote Score')
    plt.title('Comment Score vs. Time Offset (2024)')
    plt.legend(handles=[red_patch, blue_patch])

    plt.grid(True)
    plt.show()
