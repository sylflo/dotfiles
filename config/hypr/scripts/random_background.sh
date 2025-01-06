#!/bin/sh

# Specify the directory (or use the current directory by default)
DIR=/home/sylflo/.config/hypr/backgrounds

# Check if the directory exists
if [ ! -d "$DIR" ]; then
  echo "Error: Directory '$DIR' does not exist."
  exit 1
fi

# Get all files in the directory
FILES=("$DIR"/*)

# Check if there are any files in the directory
if [ ${#FILES[@]} -eq 0 ]; then
  echo "Error: No files found in the directory."
  exit 1
fi

# Get a random index
RANDOM_INDEX=$((RANDOM % ${#FILES[@]}))

# Echo the random filename
echo -n  ${FILES[$RANDOM_INDEX]}
