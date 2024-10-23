# from fastapi import FastAPI
from PIL import Image
import numpy as np
import cv2
from base64 import b64decode, b64encode
from io import BytesIO
from requests import get
# from uvicorn import run

# app = FastAPI()

def getCharacters():
    response = get("https://api.github.com/repos/mihai-ciorobitca/captcha-api/contents/api/data")
    characters = {}
    print(response.json)
    for file in response.json():
        if file["name"].endswith(".png"):
            character = get(file["download_url"])
            characters[b64encode(character.content).decode("utf-8")] = file["name"].replace(".png", "")
    return characters

def convertToBinary(img: Image):
    img = img.convert("RGB")
    px = np.array(img)
    for rows in range(px.shape[0]):
        for columns in range(px.shape[1]):
            if not np.all(px[rows, columns] == 255):
                px[rows, columns] = [0, 0, 0]
    return Image.fromarray(px).convert("L")


def extractCharacters(img: Image):
    image = np.array(img)
    contours, _ = cv2.findContours(
        image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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


def read_captcha(imageBase64: str):
    characters = getCharacters()
    imgBinary = convertToBinary(imageBase64)
    extractedCharacters = extractCharacters(imgBinary)
    captchaString = ""
    for extractedCharacter in extractedCharacters:
        extractCharacterBase64 = b64encode(
            extractedCharacter.tobytes()).decode("utf-8")
        if extractCharacterBase64 in characters:
            captchaString += characters[extractCharacterBase64]
    return captchaString


def mainFunction():
    image = Image.open("example.png")
    print(getCharacters())
    # print(read_captcha(image))

mainFunction()