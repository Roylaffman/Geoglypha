from PIL import Image, ImageDraw
import os

# Create directory if it doesn't exist
os.makedirs('C:/Users/royla/Documents/dev/graphita/images', exist_ok=True)

# Function to create a black and white abstract placeholder image
def create_placeholder(filename, width=600, height=400, pattern_type='abstract'):
    # Create a white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    if pattern_type == 'abstract':
        # Draw some abstract black shapes
        for i in range(0, width, 40):
            for j in range(0, height, 40):
                if (i + j) % 3 == 0:
                    draw.rectangle([(i, j), (i + 30, j + 30)], fill='black')
                elif (i + j) % 3 == 1:
                    draw.ellipse([(i, j), (i + 30, j + 30)], fill='black')
                else:
                    points = [(i, j), (i + 30, j), (i + 15, j + 30)]
                    draw.polygon(points, fill='black')
    
    elif pattern_type == 'lines':
        # Draw horizontal lines
        for i in range(0, height, 20):
            draw.line([(0, i), (width, i)], fill='black', width=5)
    
    elif pattern_type == 'grid':
        # Draw a grid
        for i in range(0, width, 30):
            draw.line([(i, 0), (i, height)], fill='black', width=2)
        for i in range(0, height, 30):
            draw.line([(0, i), (width, i)], fill='black', width=2)
    
    elif pattern_type == 'circles':
        # Draw concentric circles
        for i in range(10, max(width, height), 40):
            draw.ellipse([(width//2 - i, height//2 - i), (width//2 + i, height//2 + i)], 
                         outline='black', width=3)
    
    elif pattern_type == 'diagonal':
        # Draw diagonal lines
        for i in range(-height, width, 20):
            draw.line([(i, 0), (i + height, height)], fill='black', width=3)
    
    elif pattern_type == 'dots':
        # Draw a pattern of dots
        for i in range(0, width, 20):
            for j in range(0, height, 20):
                draw.ellipse([(i-5, j-5), (i+5, j+5)], fill='black')
    
    # Save the image
    image.save(filename)
    print(f"Created placeholder image: {filename}")

# Create 6 different placeholder images with different patterns
patterns = ['abstract', 'lines', 'grid', 'circles', 'diagonal', 'dots']
for i, pattern in enumerate(patterns, 1):
    create_placeholder(f'/home/ubuntu/geoglyfitia/images/placeholder{i}.png', pattern_type=pattern)
