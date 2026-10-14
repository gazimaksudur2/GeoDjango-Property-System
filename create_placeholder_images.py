import os
from PIL import Image, ImageDraw


image_types = [
    "front",
    "living",
    "bedroom",
    "kitchen"
]


property_ids = range(1, 1301)


for pid in property_ids:

    folder = f"media/properties/{pid}"

    os.makedirs(
        folder,
        exist_ok=True
    )

    for img_type in image_types:
        path = f"{folder}/{img_type}.jpg"

        if not os.path.exists(path):
            img = Image.new(
                "RGB",
                (512, 512),
                color=(220, 220, 220)
            )

            draw = ImageDraw.Draw(img)
            draw.text(
                (120, 240),
                f"Property {pid}\n{img_type}",
                fill=(0, 0, 0)
            )
            img.save(path)

print("Placeholder images created")