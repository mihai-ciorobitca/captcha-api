from fastapi import FastAPI
from PIL import Image
import numpy as np
from os import listdir
import cv2
from base64 import b64decode
from io import BytesIO

app = FastAPI()

def convertToBinary(imageBase64):
    img = Image.open(BytesIO(b64decode(imageBase64))).convert("RGB")
    px = np.array(img)
    for rows in range(px.shape[0]):
        for columns in range(px.shape[1]):
            if not np.all(px[rows, columns] == 255):
                px[rows, columns] = [0, 0, 0]
    return Image.fromarray(px).convert("L")

def extractCharacters(img):
    image = np.array(img)
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objects = []
    contoursSorted = sorted(contours, key=lambda x: cv2.boundingRect(x)[0])
    mask = np.zeros_like(image)
    for contour in contoursSorted:
        cv2.drawContours(mask, [contour], 0, color=255, thickness=-1) 
        # 0 is the index of contour and tickeness is set to -1 so that it fills the contour
        object_extracted = cv2.bitwise_and(image, image, mask=mask)
        x, y, w, h = cv2.boundingRect(contour)
        object_cropped = object_extracted[y:y+h, x:x+w]
        object_pil = Image.fromarray(object_cropped)
        objects.append(object_pil)
    return objects

@app.post("/captcha")
async def read_captcha(imageBase64: str):
    characters = listdir("data")
    charactersImages = [Image.open("data/" + file) for file in characters]
    imgBinary = convertToBinary(imageBase64)
    extractedCharacters = extractCharacters(imgBinary)
    captchaString = ""
    for extractedCharacter in extractedCharacters:
        for index, characterImage in enumerate(charactersImages):
            if np.array_equal(np.array(extractedCharacter), np.array(characterImage)):
                captchaString += characters[index].replace(".png", "")
    return {"captcha": captchaString}

@app.get("/")
async def root():  
    characters = listdir("data")
    return {"characters": characters}

app.run(host="0.0.0.0", port=8000)

