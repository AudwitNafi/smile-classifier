from fastapi import FastAPI, File, UploadFile, HTTPException, Request
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
from models import history


app = FastAPI(title = "Smile Classifier")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind=engine)

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

        model_path = 'model/finalized_model.sav'
        loaded_model = pickle.load(open(model_path, 'rb'))
        img = cv2.imread(output_file_path)    
        resize = tf.image.resize(img, (256, 256))
        yhat = loaded_model.predict(np.expand_dims(resize / 255, 0))
        result = "smiling" if yhat > 0.5 else "not smiling"
        session = SessionLocal()
        record = history(title=output_file_path, result=result, date_time=datetime.utcnow())
        session.add(record)
        session.commit()
        image_id = record.id
        session.close()

        # return {"result": result, "image_id": image_id, "url": f"/classify/{image_id}"}
        return RedirectResponse(url=f"/classify/{image_id}", status_code=303)
        
        # return {"message": f"Image saved as {output_file_path}"}
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")


@app.get("/classify/{image_id}", response_class=HTMLResponse)
async def classify_image(image_id: int):
    # image = Image.open(image_path)
    session = SessionLocal()
    record = session.query(history).filter(history.id == image_id).first()
    session.close()
    if record:
        return f"""<h1>Classification Result</h1>
        <p>Image Path: {record.title}</p>
        <p>Result: {record.result}</p>
        <p>Date-Time: {record.date_time}</p>"""
    else:
        return "<h1>Record not found</h1>"


    # return {"message": f"{yhat}"}

@app.get("/history")
async def classify_page(request: Request):
    session = SessionLocal()
    ##query to retrieve all history
    result = session.query(history).all()
    session.close()
    #printing all rows for testing purposes
    for record in result:
        print(record.id, record.title, record.result, record.date_time)
    
    return templates.TemplateResponse("history.html", {"request": request, "result": result})