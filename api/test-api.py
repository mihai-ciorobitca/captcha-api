from requests import post 
from PIL import Image
from base64 import b64encode
from io import BytesIO

url = "https://captcha-api.vercel.app/solve-captcha"

img = Image("captcha.png")

buffered = BytesIO()
img.save(buffered, format="PNG")
imgBase64 = b64encode(buffered.getvalue()).decode("utf-8")

response = post(url, json={"image": imgBase64})

