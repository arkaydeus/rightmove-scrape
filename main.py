import json
from optparse import Option
from typing import Optional
from urllib import response

import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

#  The following allows the vercel hosted version to accept requests that are not originating from Vercel
#  in a browser

#  CORS origins
# origins = [
#     "http://localhost:3000",
#     "https://localhost:3000",
#     "https://perfections-web.vercel.app",
# ]

# Add middleware adapter to prevent blocking
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RightMove(BaseModel):
    url: str


def load_data() -> dict:

    """Opens perfections.json and returns the dict version of the data

    Returns:
        _type_: dictionary of perfection data

    """
    with open("data/perfections.json", "r", encoding="utf-8") as f:
        file_data: str = f.read()
        file_dict: dict = json.loads(file_data)
    return file_dict


@app.get("/")
def read_root():
    return {"status": "live"}


@app.post("/rightmove/")
def post_url(rightmove: RightMove):
    response = requests.get(rightmove.url)
    if not response.ok:
        return {"status": "failed"}

    soup = BeautifulSoup(response.text, "html.parser")
    street: Optional[PageElement] = soup.find("h1", {"itemprop": "streetAddress"})
    price: Optional[PageElement] = soup.find("div", {"style": "font-size:24px"})

    if street and price:
        return {"street": street.get_text(), "price": price.get_text()}

    else:
        return {"status": "parsing error"}
    # return load_data()
