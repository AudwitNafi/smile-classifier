from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from PIL import Image
import os
import io
import cv2
import tensorflow as tf
import pickle
import numpy as np
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title = "Smile Classifier")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/")
async def post():
    return "The post route."

@app.get("/classify")
async def classify_page(request: Request):
    return templates.TemplateResponse("classify.html", {"request": request})

@app.post("/classify")
async def upload_image(file: UploadFile):
    # Validate the file is an image
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG are supported.")

    # Create a unique file name for the JPG image
    output_file_path = os.path.join("images", f"{os.path.splitext(file.filename)[0]}.jpg")

    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Open the image using Pillow
        with Image.open(io.BytesIO(contents)) as img:
            # Convert to RGB (if necessary) and save as JPG
            rgb_image = img.convert("RGB")
            rgb_image.save(output_file_path, format="JPEG")
        
        return {"message": f"Image saved as {output_file_path}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")


@app.get("/classify/{image_path}")
async def classify_image(image_path: str):
    # image = Image.open(image_path)
    model_path = 'model/finalized_model.sav'
    loaded_model = pickle.load(open(model_path, 'rb'))
    img = cv2.imread(image_path)    
    resize = tf.image.resize(img, (256, 256))
    yhat = loaded_model.predict(np.expand_dims(resize / 255, 0))
    if yhat > 0.5:
        return {"message" : "This Person is Smiling!"}
    else:
        return {"message" : "This Person is Not Smiling!"}

    # return {"message": f"{yhat}"}

@app.get("/history")
async def classify_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})