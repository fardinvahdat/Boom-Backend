import cv2
import numpy as np
import torch
from RRDBNet_arch import RRDBNet
from app.config import settings

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize ESRGAN model
model = RRDBNet(3, 3, 64, 23, gc=32)
model.load_state_dict(torch.load(
    'models/RRDB_ESRGAN_x4.pth', map_location=device))
model.eval()
model = model.to(device)


async def enhance_image(input_path: str, output_path: str):
    """Enhance an image using ESRGAN model"""
    try:
        # Read and process image
        img = cv2.imread(input_path, cv2.IMREAD_COLOR)
        img = img * 1.0 / 255
        img = torch.from_numpy(np.transpose(
            img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_LR = img.unsqueeze(0).to(device)

        # Enhance image
        with torch.no_grad():
            output = model(img_LR).data.squeeze(
            ).float().cpu().clamp_(0, 1).numpy()

        # Save output
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round().astype(np.uint8)
        cv2.imwrite(output_path, output)

        return True
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return False
