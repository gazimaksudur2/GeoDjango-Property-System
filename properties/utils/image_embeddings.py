from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch


model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)


def generate_image_embedding(image_path):
    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model.get_image_features(
            **inputs
        )

    if hasattr(outputs, "image_embeds"):
        embedding = outputs.image_embeds

    elif hasattr(outputs, "pooler_output"):
        embedding = outputs.pooler_output

    else:
        embedding = outputs

    embedding = (
        embedding
        .cpu()
        .numpy()[0]
        .tolist()
    )

    return embedding
