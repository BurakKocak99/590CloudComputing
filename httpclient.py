from requests_html import HTMLSession
from PIL import Image
import concurrent.futures
import queue

imageName = "woman.jpg"

sessionList = []
for i in range(30):
    sessionList.append(HTMLSession())

image = Image.open("woman.jpg")

#bytes = image_to_byte_array(image)



'''for i in range(30):
    browser= sessionList[i].post("http://localhost:8080",imageBytes)

'''
QUEUE = queue.Queue()


def makeSessions(n=10):
    for _ in range(n):
        QUEUE.put(HTMLSession())


def getSession(block=True):
    return QUEUE.get(block=block)

def freeSession(session):
    if isinstance(session, HTMLSession):
        QUEUE.put(session)


def getURLs(imageBytes):
    urls = []
    session = getSession()
    try:
        response = session.post("http://localhost:8080", imageBytes)
        response.raise_for_status()
        response.html.render()
    finally:
        freeSession(session)
    return urls

def cleanup():
    while True:
        try:
            getSession(False).close()
        except queue.Empty:
            break


def processURL(url, imageBytes):
    session = getSession()
    try:
        response = session.post(url,imageBytes)
        response.raise_for_status()
        response.html.render()
    finally:
        freeSession(session)


if __name__ == '__main__':
    with open(imageName, 'rb') as document:
        imageBytes = bytearray(document.read())
    try:
        makeSessions()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(processURL, "http://localhost:8080",imageBytes) for url in range(100)]
            for _ in concurrent.futures.as_completed(futures):
                pass
    finally:
        cleanup()

