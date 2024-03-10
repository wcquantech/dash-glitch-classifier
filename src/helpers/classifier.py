import os
import torch
from PIL import Image
import torch.nn.functional as F
import torchvision.transforms as transform

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
project_directory = os.path.dirname(current_directory)

# Model configurations
config_inception = {
    # The path is relative to the project directory
    "model": os.path.join(project_directory, "models", "inception-v3_checkpoint.pt"),
    "transforms": transform.Compose([
        transform.Resize([299, 299]),
        transform.ToTensor(),
        transform.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ]),
}

config_googlenet = {
    # The path is relative to the project directory
    "model": os.path.join(project_directory, "models", "google-net_checkpoint.pt"),
    "transforms": transform.Compose([
        transform.Resize([224, 224]),
        transform.ToTensor(),
        transform.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ]),
}



def classify(model_name, imgsrc, class_list):
    cfg = config_inception if model_name == "Inception-V3" else config_googlenet
    classes = class_list[:]
    transforms = cfg["transforms"]
    img = Image.open(imgsrc)
    input = transforms(img).unsqueeze(0)
    
    model = torch.load(cfg["model"], map_location=torch.device("cpu"))
    model.eval()

    output = model(input)
    _, pred = torch.max(output, 1)
    softmaxed = F.softmax(output[0], dim=0).tolist()

    prob_1 = max(softmaxed)
    if prob_1 >= 0.8:
        return classes[pred[0]], prob_1, None
    else: 
        idx = softmaxed.index(prob_1)
        softmaxed.pop(idx)
        classes.pop(idx)
        prob_2 = max(softmaxed)
        return classes[pred[0]], prob_1, [prob_2, classes[softmaxed.index(prob_2)]]