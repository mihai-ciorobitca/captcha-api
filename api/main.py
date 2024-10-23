from fastapi import FastAPI
from PIL import Image
import numpy as np
import cv2
from base64 import b64decode, b64encode
from io import BytesIO
from requests import get
from uvicorn import run

app = FastAPI()

characters = {
    'iVBORw0KGgoAAAANSUhEUgAAABYAAAAnCAAAAAAu+efvAAAAYUlEQVR4nO2TMRaAMAhDE+5/ZxyQSiH6HB1kgg8NDCmwwv3KeaIGuMNENig8Wl7EsmA292HrNArrNF7YQOsSEaY0nqZ//AnsGr8UcUhrAqCx83SqduwUobQmcft36q4idgD89xdAUdWvkgAAAABJRU5ErkJggg==': '0',
    'iVBORw0KGgoAAAANSUhEUgAAAAgAAAAnCAAAAAAXnla0AAAAKklEQVR4nM3OIQ4AIAADsY7//3kIQrA4mKqYuBRIoBiQDa+RPzIO1np3ngvcA0uhzvuwAAAAAElFTkSuQmCC': '1',
    'iVBORw0KGgoAAAANSUhEUgAAABUAAAAnCAAAAADFzlzsAAAAfklEQVR4nLXTQQ4EIQhE0V/c/841m2lEYNGbdmN8IWUiKMA8S2U/+ojO0YdFWwYRXQWeCrCoVgX8NuErNehlrTc16+uARq23d/jjrdmqnquhzobFhkVr/6OihlZM9TUaMUNTr9Caq1HrPm+xITFuOrl9XmMrRRW1amKMLwDwA1YoGUmiQcGlAAAAAElFTkSuQmCC': '2',
    'iVBORw0KGgoAAAANSUhEUgAAABMAAAAnCAAAAADI0CyrAAAAXklEQVR4nM2SMQ7AIAwDz6j//7I7IAIkdKYMQRy2iExkYmnsCxt83OEJtcsMohWrM9veWt0n3SWmzFx1BiFmJN0JraLPDJxIzbT0oihJ+aP8rv5HCKDP6WGen3QGeAGPPRFGMTnGBwAAAABJRU5ErkJggg==': '3',
    'iVBORw0KGgoAAAANSUhEUgAAABYAAAAlCAAAAABjMUbkAAAAXUlEQVR4nM2RQQ7AIAgEB///5+1BogGxNr20ezKTETYBRqT5bpNChSmxwB7bUT7YSXasjZ3kjsMIlSuFHOd9twULeW9X8iiYYivCagy0da5/iOkNTrf8ENtvmrzBFzC4EkDfsOBbAAAAAElFTkSuQmCC': '4',
    'iVBORw0KGgoAAAANSUhEUgAAABIAAAAnCAAAAAAnEkeVAAAAU0lEQVR4nNWQMRLAMAjDZC7//7I7tAMxGTq2bAjMcRJmL1USWG3ckbatGoQap36O1ORooodG0IYKMzhdeQYPt16+qo/4SuTXojOG1Lt75+B+RQ9cUcIMT7r4RuEAAAAASUVORK5CYII=': '5',
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAnCAAAAAAqDDfSAAAAa0lEQVR4nMXSQQ6AIAxE0T/G+195XIDYFmLCRrvjwdCkqWhlRomzSOdBCuh0buiJ4KjwhlN6L/4jKg1ygeOixr380y2uSvWlAE/xZSME/nJKdZN2/0x5gw5lDaNzNMWl7aXFgolbnCy2fW4uOMQYQa9/DuEAAAAASUVORK5CYII=': '6',
    'iVBORw0KGgoAAAANSUhEUgAAABUAAAAnCAAAAADFzlzsAAAAZElEQVR4nI3RSw7AIAgE0MH735kurJUy/FiRyRMSFCioZHEGqNzWYobZBFCqgHAaWgUkmBDZTUf2pRN76MB+tLeXttbQzlpqrbD9//8K3tfbHK2sp4UlmlumqQ1oZiOaWH/DXQ+NTRZHoU/n8gAAAABJRU5ErkJggg==': '7',
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAnCAAAAAAqDDfSAAAAdklEQVR4nL2SQQoFMQhDX7z/nTMLS5mqA93830XBhwk2VuQxgFahTV5AJ0oSlWGQX17LSXEyBDiKGAENklATHDvvYZ3+Vm5QlEQMGlJKeNLxmR5HMiivo1Hhnmf3VIb8i+j+Bi92tKKr60DqahEtD33/+e21iweXTBxD3OtMtwAAAABJRU5ErkJggg==': '8',
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAnCAAAAAAqDDfSAAAAbElEQVR4nN3SSRLAIAhE0d/c/86dRdQoYlWyDSt9ijhBD3s0dcPa10INIhkGdJsWCmZrq4Vna81YDQQOijihKixnusL3hfb82K5ppCfVofq++fwcE6aBPddfT/QfNCijQcXVaXzaJ0R6o552ASSIGD3UjG2FAAAAAElFTkSuQmCC': '9',
    'iVBORw0KGgoAAAANSUhEUgAAABkAAAAcCAAAAACxT0sMAAAAbUlEQVR4nL2QSRbAIAhDE573vzJdOJRo6rKsCD8MSgBI9CBKsBKhxZZakQEdj1JshKt3Jy86yIq/SJtJWnJU5zQLEF8ADQn9vWmMHcgeC+4v9S2X245pWUk6gKDIYqLbQ3cblwpRw5Vv2iVl1wOqihc1Z7ZxSQAAAABJRU5ErkJggg==': 'a',
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAnCAAAAAAqDDfSAAAAbklEQVR4nNWRSwoAIQxDX8rc/8qZhd+qG3czgiCPtMFEGAAxHXklQBwYcWDERj4E7f58GqpXQzlUrtCMwSrPyZUNkRgCXOCUUzfKqYOvfvSX5H2CFzvTvEFBpq2jmZY6tHmrRLcmXztSYrPtWPQCPboaSAvRw4wAAAAASUVORK5CYII=': 'b',
    'iVBORw0KGgoAAAANSUhEUgAAABAAAAAcCAAAAABNWmDGAAAAQElEQVR4nN2RMQ4AIAgDr/7/z3XABEETdztAejQMIEJeHRUXwNsIhNMAyMXCoOkG9Ez8BPxMVJ1Hzh3K2h5FYRPHFwos/xI1SQAAAABJRU5ErkJggg==': 'c',
    'iVBORw0KGgoAAAANSUhEUgAAABkAAAAnCAAAAADf8rxiAAAAc0lEQVR4nNWSwQ7AIAhDKfH/f5kd5ixtvHkw86Dia8BQEG3Ve6DtBhERkUawpE64/k7KyOBraa+GqKuxtDQM0Lq7QOs1KGS20ljqqHun/vgonGW7T9zMwzp7UxOKeE2Nmwa7v31zoJaKp4ymSsapTeHM/gDcwBdPSAdzDgAAAABJRU5ErkJggg==': 'd',
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAcCAAAAABEscC8AAAAXklEQVR4nK3Ryw6AIAxE0TuN///L4wKoFlygsSs4mfJIYZSdSzWoexXqEJNhQM1UKACke7MJX7FsCaYSOGqw1ZJ8RAPyTvIV6vj+pH9w/dN+u/pYJhxnqmC9StTZJp5OiBIwqLub/QAAAABJRU5ErkJggg==': 'e',
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAmCAAAAADhUOR3AAAAT0lEQVR4nM3SMQoAIAxD0R/x/lfWQdFaOjgU1EV5BJqCwpw2b3mweIS0TDtZApt42kA7xCYzUQTLVD8ZoLrQfrWofHLPHFSEbyv9hMDlr+sQ4gpHfFx6uwAAAABJRU5ErkJggg==': 'f'
}
def convertToBinary(imgBase64: str):
    img = Image.open(BytesIO(b64decode(imgBase64)))
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
    imgBinary = convertToBinary(imageBase64)
    extractedCharacters = extractCharacters(imgBinary)
    captchaString = ""
    for extractedCharacter in extractedCharacters:
        buffered = BytesIO()
        extractedCharacter.save(buffered, format="PNG")
        extractedCharacterBase64 = b64encode(buffered.getvalue()).decode("utf-8")
        if extractedCharacterBase64 in characters:
            captchaString += characters[extractedCharacterBase64]
    return captchaString

@app.route('/solve-captcha', methods=['POST'])
def mainFunction(imageBase64: str):
    return {"captcha": read_captcha(imageBase64)}


if __name__ == "__main__":
    run()
