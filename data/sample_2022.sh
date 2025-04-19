#!/bin/bash

# Step 1: List all chunk files for 2022
chunks=(chunk_2022_*)
total_chunks=${#chunks[@]}

# Step 2: Calculate how many lines to take per file
lines_per_chunk=$((1000 / total_chunks))
remainder=$((1000 % total_chunks))

# Step 3: Create output file
output_file="sample_2022_1000.txt"
> "$output_file"  # Clear or create the file

# Step 4: Loop over each chunk file
for i in "${!chunks[@]}"; do
    chunk="${chunks[$i]}"
    lines_to_take=$lines_per_chunk

    # Distribute the remainder (for uneven division)
    if [ $i -lt $remainder ]; then
        lines_to_take=$((lines_per_chunk + 1))
    fi

    head -n $lines_to_take "$chunk" >> "$output_file"
done

echo "✅ Sampled 1000 lines across ${total_chunks} chunks into $output_file"

