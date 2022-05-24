import json
from optparse import Option
from typing import List, Optional
from urllib.parse import unquote_plus

import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

#  The following allows the vercel hosted version to accept requests that are not originating from Vercel
#  in a browser


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


def rightmove_data(url: str):
    response = requests.get(url)
    if not response.ok:
        return {"status": "failed"}

    soup = BeautifulSoup(response.text, "html.parser")
    street: Optional[str] = None
    try:
        street_element: Optional[PageElement] = soup.find(
            "h1", {"itemprop": "streetAddress"}
        )
        if street_element:
            street = street_element.get_text()
    except:
        return {"status": "cannot find street"}

    articles: List[PageElement] = soup.find_all("article")

    try:
        price = [item for item in list(articles[1].stripped_strings) if item[0] == "£"][
            0
        ]
    except:
        return {"status": "cannot find price"}

    try:
        tel = list(soup.select("a[href*=tel]")[0].stripped_strings)[2]
    except:
        return {"status": "cannot phone number"}

    agent: Optional[str] = None
    try:
        agent_element: Optional[PageElement] = soup.find("p", text="MARKETED BY")
        if agent_element and agent_element.next_sibling:
            agent = list(agent_element.next_sibling.stripped_strings)[0]
    except:
        return {"status": "cannot find agent"}

    if all([street, price, tel, agent]):
        return {"street": street, "price": price, "agent": agent, "tel": tel}

    else:
        return {"status": "parsing error"}


@app.post("/rightmove/")
def post_url(rightmove: RightMove):
    return rightmove_data(rightmove.url)


@app.get("/rightmove/")
def get_url(url: str):
    headers = {"Cache-Control": "max-age=0, s-maxage=86400"}
    return JSONResponse(content=rightmove_data(url), headers=headers)
