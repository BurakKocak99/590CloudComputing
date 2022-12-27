from requests_html import HTMLSession
from PIL import Image
import concurrent.futures
import queue
imageName = "woman.jpg"

seassion = HTMLSession()

with open(imageName, 'rb') as document:
    imageBytes = bytearray(document.read())

browser = seassion.post("http://localhost:8080", imageBytes)
print(browser.text)