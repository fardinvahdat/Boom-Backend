from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime, timedelta

from app.schemas.user import UserInDB
from app.services.auth import get_current_user
from app.utils.image_processing import enhance_image

router = APIRouter()


@router.post("/enhance")
async def enhance_user_image(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    temp_path = f"temp_{uuid.uuid4()}.jpg"
    result_path = f"enhanced_{uuid.uuid4()}.png"

    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # Process image
        success = await enhance_image(temp_path, result_path)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to process image"
            )

        return FileResponse(result_path, media_type="image/png")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
    finally:
        # Clean up temporary files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(result_path):
            os.remove(result_path)
