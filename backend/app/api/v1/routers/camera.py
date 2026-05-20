from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from app.core.dependencies import get_db
from app.models.camera import Camera
from app.models.enums import CameraStatus

router = APIRouter(prefix="/cameras", tags=["Cameras"])


router = APIRouter(
    prefix="/cameras",
    tags=["Cameras"]
)

UPLOAD_DIR = "uploads"

Path(UPLOAD_DIR).mkdir(exist_ok=True)


@router.post("/")
def create_camera(
    camera_name: str = Form(...),
    street_id: int = Form(...),
    location_id: int = Form(...),

    status: CameraStatus = Form(CameraStatus.ACTIVE),

    video_url: str = Form(None),

    video_file: UploadFile = File(None),

    db: Session = Depends(get_db)
):

    saved_video = None

    # SAVE MP4
    if video_file:

        file_path = f"{UPLOAD_DIR}/{video_file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        saved_video = file_path

    camera = Camera(
        camera_name=camera_name,
        street_id=street_id,
        location_id=location_id,
        status=status,

        video_url=video_url,
        video_file=saved_video
    )

    db.add(camera)

    db.commit()

    db.refresh(camera)

    return camera


@router.get("/")
def get_cameras(
    db: Session = Depends(get_db)
):
    return db.query(Camera).all()