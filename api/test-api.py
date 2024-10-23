from requests import post 

url = "https://captcha-api.vercel.app/solve-captcha"

response = post(url)

print(response.status_code)
print(response.json())