import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from app.services.auth import get_current_user
from app.schemas.user import UserInDB
from app.utils.image_processing import enhance_image

router = APIRouter()


@router.post("/enhance")
async def enhance_user_image(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    # Create temp directory if it doesn't exist
    os.makedirs("temp_images", exist_ok=True)

    temp_path = f"temp_images/temp_{uuid.uuid4()}.jpg"
    result_path = f"temp_images/enhanced_{uuid.uuid4()}.png"

    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process image
        success = await enhance_image(temp_path, result_path)
        if not success or not os.path.exists(result_path):
            raise HTTPException(
                status_code=500,
                detail="Failed to process image"
            )

        return FileResponse(
            result_path,
            media_type="image/png",
            filename="enhanced_image.png"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
    finally:
        # Clean up only after successful response
        if os.path.exists(temp_path):
            os.remove(temp_path)
        # Don't delete result_path here - FileResponse needs it
