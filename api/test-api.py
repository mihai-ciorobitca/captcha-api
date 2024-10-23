from requests import post 
from PIL import Image
from base64 import b64encode
from io import BytesIO

url = "http://127.0.0.1:8000/solve-captcha"

img = Image.open("captcha.png")

buffered = BytesIO()
img.save(buffered, format="PNG")
imgBase64 = b64encode(buffered.getvalue()).decode("utf-8")

response = post(url, json={"captcha": imgBase64})

print(response.text)
