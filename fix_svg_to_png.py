import re
import base64
import subprocess
import os

with open("architecture-target.drawio", "r") as f:
    xml = f.read()

# Find all SVG base64 strings
svgs = re.findall(r'data:image/svg\+xml%3Bbase64,([A-Za-z0-9+/=]+)', xml)
print(f"Found {len(svgs)} SVG images")

for i, svg_b64 in enumerate(set(svgs)):
    svg_data = base64.b64decode(svg_b64)
    with open(f"/tmp/icon_{i}.svg", "wb") as f:
        f.write(svg_data)
    
    # Convert to PNG using ImageMagick
    subprocess.run(["magick", "-background", "none", "-density", "300", f"/tmp/icon_{i}.svg", f"/tmp/icon_{i}.png"])
    
    if os.path.exists(f"/tmp/icon_{i}.png"):
        with open(f"/tmp/icon_{i}.png", "rb") as f:
            png_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        # Replace in XML
        # We need to replace exactly this base64 string
        # using data:image/png%3Bbase64,...
        old_str = f"data:image/svg+xml%3Bbase64,{svg_b64}"
        new_str = f"data:image/png%3Bbase64,{png_b64}"
        xml = xml.replace(old_str, new_str)
        print(f"Replaced SVG {i} with PNG")
    else:
        print(f"Failed to convert SVG {i}")

with open("architecture-target.drawio", "w") as f:
    f.write(xml)

with open("diagrams/target-observability-aiops-architecture.drawio", "w") as f:
    f.write(xml)

print("Done")
