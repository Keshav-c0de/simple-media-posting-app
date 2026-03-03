from dotenv import load_dotenv
from imagekitio import ImageKit
import os 


if load_dotenv():
    print("*"*100)


image_kit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    )
URL_ENDPOINT = os.environ.get("IMAGEKIT_URL_ENDPOINT")