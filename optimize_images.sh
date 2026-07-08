#!/bin/bash

# Make sure we are in the right directory
cd "$(dirname "$0")"

echo "🎨 Starting image optimization..."

# Check if there are any PNGs to process
count=$(ls -1 bilder/*.png 2>/dev/null | wc -l)
if [ "$count" -eq 0 ]; then
    echo "✨ No new PNG images found in 'bilder/' to optimize."
    exit 0
fi

echo "📦 Found $count PNG image(s). Compressing to lightweight JPEGs..."

for f in bilder/*.png; do 
    # Extract filename without extension
    filename=$(basename "$f" .png)
    
    # Skip if JPG already exists AND is newer than the PNG
    if [ -f "bilder/$filename.jpg" ] && [ "bilder/$filename.jpg" -nt "$f" ]; then
        echo "  -> ⏭️ Skipping $filename.png (optimized JPG is already up to date)"
        continue
    fi
    
    echo "  -> 🗜️ Optimizing $filename.png..."
    
    # Use macOS built-in sips tool to resize (max width 1600px) and compress (75% quality JPEG)
    sips -Z 1600 -s format jpeg -s formatOptions 75 "$f" --out "bilder/$filename.jpg" > /dev/null 2>&1
done

echo "✅ All new images optimized successfully!"
echo "   (You can now run 'python3 convert_book.py' to update the offline PWA cache with the new images)"
