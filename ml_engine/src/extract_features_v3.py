# dino_feature_extraction.py
import torch
from transformers import AutoModel, AutoImageProcessor
from numpy.linalg import norm
import numpy as np
import os
import threading
from PIL import Image
from crop_images import extract_and_crop_image

# Use CUDA (GPU) if available, otherwise CPU
if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"
print(f"Using device: {DEVICE}")

# DINOv3 base model
MODEL_ID = "facebook/dinov3-vitb16-pretrain-lvd1689m"
FEATURE_DIM = 768

model = None
processor = None
_model_lock = threading.Lock()

def get_dino_components():
    """Thread-safe lazy loader for DINOv3 model and processor."""
    global model, processor
    
    with _model_lock:
        if model is not None and processor is not None:
            return model, processor

        os.environ['HF_HOME'] = os.path.expanduser('~/.cache/huggingface')
        
        # Load standard AutoModel
        loaded_model = AutoModel.from_pretrained(MODEL_ID).to(DEVICE)
        loaded_processor = AutoImageProcessor.from_pretrained(MODEL_ID)
        
        model = loaded_model
        processor = loaded_processor
        return model, processor

# Function to extract DINOv3 features from an image
def extract_features(img_path, return_cropped_image=False):
    # This will now throw a loud error if the model fails to load
    current_model, current_processor = get_dino_components()
        
    try:
        image = None
        try:
            # 1. Load and crop the image using YOLO
            image = extract_and_crop_image(img_path)
        except Exception as e:
            print(f"Error during YOLO cropping: {e}. Will fall back to full image.")

        if image is None or not hasattr(image, "shape") or image.size == 0:
            image = np.array(Image.open(img_path).convert("RGB"))

        # 2. Process the image
        inputs = current_processor(images=image, return_tensors="pt").to(DEVICE)
        
        # 3. Run the model
        with torch.no_grad():
            outputs = current_model(**inputs)
            
        # 4. Get the feature vector (CLS token is index 0)
        feature_vector = outputs.last_hidden_state[:, 0].squeeze().cpu().numpy()
            
        # 5. Normalize the vector
        normalized_vector = feature_vector / norm(feature_vector)

        if return_cropped_image:
            return (img_path, normalized_vector, image)
        return (img_path, normalized_vector)
        
    except Exception as e:
        print(f"Failed to extract DINOv3 features for {img_path}: {e}")
        if return_cropped_image:
            return (img_path, e, None)
        return (img_path, e)