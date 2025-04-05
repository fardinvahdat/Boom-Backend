import cv2
import numpy as np
import torch
from RRDBNet_arch import RRDBNet
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize model
model = RRDBNet(3, 3, 64, 23, gc=32)
model.load_state_dict(torch.load(
    'models/RRDB_ESRGAN_x4.pth', map_location=device))
model.eval()
model = model.to(device)


async def enhance_image(input_path: str, output_path: str) -> bool:
    try:
        # Read image
        img = cv2.imread(input_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not read image file")

        # Convert and normalize
        img = img * 1.0 / 255
        img = torch.from_numpy(np.transpose(
            img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_LR = img.unsqueeze(0).to(device)

        # Enhance
        with torch.no_grad():
            output = model(img_LR).data.squeeze(
            ).float().cpu().clamp_(0, 1).numpy()

        # Save output
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round().astype(np.uint8)
        cv2.imwrite(output_path, output)

        return os.path.exists(output_path)
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return False
