from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends
from PIL import Image
import os
import io
import cv2
import tensorflow as tf
import pickle
import numpy as np
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from models import history


app = FastAPI(title = "Smile Classifier")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images/", StaticFiles(directory="images"), name="images")
app.mount("/meme_images/", StaticFiles(directory="meme_images"), name="meme_images")
models.Base.metadata.create_all(bind=engine)

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/classify")
async def classify_page(request: Request):
    return templates.TemplateResponse("classify.html", {"request": request})

@app.post("/classify")
async def upload_image(file: UploadFile, session:Session=Depends(get_db)):
    
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG are supported.")
    print(file.filename)
    
    output_file_path = "images/" + file.filename

    try:
        contents = await file.read()
        with Image.open(io.BytesIO(contents)) as img:
            # Convert to RGB (if necessary) and save as JPG
            rgb_image = img.convert("RGB")
            rgb_image.save(output_file_path, format="JPEG")

        # loading model and predicting
        model_path = 'model/finalized_model.sav'
        loaded_model = pickle.load(open(model_path, 'rb'))
        img = cv2.imread(output_file_path)    
        resize = tf.image.resize(img, (256, 256))
        yhat = loaded_model.predict(np.expand_dims(resize / 255, 0))
        result = "smiling" if yhat > 0.5 else "not smiling"

        record = history(title=output_file_path, result=result, date_time=datetime.now())
        session.add(record)
        session.commit()
        image_id = record.id
        session.close()
        return RedirectResponse(url=f"/classify/{image_id}", status_code=303)
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")


@app.get("/classify/{image_id}", response_class=HTMLResponse)
async def classify_image(image_id: int, request: Request, session:Session=Depends(get_db)):
    record = session.query(history).filter(history.id == image_id).first()
    session.close()
    if record:
        return templates.TemplateResponse("classification.html", {"request": request, "record": record})
    else:
        return "<h1>Record not found</h1>"


@app.get("/history")
async def classify_page(request: Request, session:Session=Depends(get_db)):
    result = session.query(history).all()
    session.close()
    return templates.TemplateResponse("history.html", {"request": request, "result": result})