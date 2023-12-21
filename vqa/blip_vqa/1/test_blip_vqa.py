import numpy as np
import torch


from models.blip_vqa import blip_vqa

image_urls = np.array(
    [
        b"/workspace/examples/beach.jpg",
        b"/workspace/examples/beach.jpg",
        b"/workspace/examples/merlion.png",
        b"/workspace/examples/merlion.png",
    ]
)
print(image_urls)
questions = np.array(
    [
        b"where is the woman sitting?",
        b"where is the dog sitting?",
        b"",
        b"which city is this photo taken?",
    ]
)
print(questions)


model_url = "/workspace/model_base_vqa_capfilt_large.pth"
# model_url = "https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_vqa_capfilt_large.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = blip_vqa(pretrained=model_url)
model.eval()
model = model.to(device)

with torch.no_grad():
    answers = model(image_urls, questions, enable_modal_level_batch=True)
print(answers)
with torch.no_grad():
    answers = model(image_urls, questions, enable_modal_level_batch=False)
print(answers)