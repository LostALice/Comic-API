# Code by AkinoAlice@Tyrant_Rex

import requests, aiohttp, asyncio, base64
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from os import path,makedirs

class nhentai:
    def __init__(self, code: int):
        """
        Get the doujinshi information from nhentai.net

        Args:
            code (int): /g/<code>

        self.info = All information

        {
            "parodies" : "Parodies"
            "tag" : "Tags"
            "artists" : "Artists"
            "groups" : "Groups"
            "languages" : "Languages"
            "categories" : "Categories"
            "pages" : "Pages"
            "code" : "Code"
        }

        """
        self.code = code
        self.comic_set = {}

        if not isinstance(code, int):
            raise BaseException("Value should be integer")

        ua = UserAgent()
        header = {'user-agent': ua.random}
        html = requests.get(f"https://nhentai.net/g/{code}/",headers=header)
        if html.status_code == 404:
            raise BaseException("404 Not Found")

        soup = BeautifulSoup(html.text, "lxml")
        page = soup.find_all(class_="tag-container field-name")

        json = {"Code": code}
        for p in page:
            attr = p.contents[0].replace("\n\t\t\t\t\t\t\t\t", "").replace(":", "")
            tags = p.find_all("span", attrs={"class": "name"})

            for tag in tags:
                tag_ = tag.text.split("|")
                if attr in json:
                    json[attr].append(tag_)
                else:
                    tag_ = tag.text.split("|")
                    json[attr] = list(tag_)

        time = soup.find_all("time", attrs={"class": "nobold"})
        json["Uploaded"] = [time[0].text]

        info_staff = ["Parodies","Tags","Artists","Groups","Languages","Categories","Pages","Uploaded"]
        for staff in info_staff:
            if not staff in json:json[staff] = None

        self.info = json
        self.parodies = json["Parodies"]
        self.tag = json["Tags"]
        self.artists = json["Artists"]
        self.groups = json["Groups"]
        self.languages = json["Languages"]
        self.categories = json["Categories"]
        self.pages = json["Pages"]
        self.uploaded = json["Uploaded"]

    def image(self,thumbnail=False):
        self.comic_set = {}
        """
        Get the doujinshi base64 encoded string from nhentai.net

        Returns:
           self.comic_set: {"path":"base64 string"}
        """
        code = self.code
        pages = BeautifulSoup(requests.get(f"https://nhentai.net/g/{code}/").text, "lxml").find_all(class_="thumb-container")
        image = [page.find_all("img", attrs={"class": "lazyload"})[0]["data-src"] for page in pages]

        async def main(image):
            global tasks
            async with aiohttp.ClientSession() as session:
                tasks = [asyncio.create_task(fetch(link, session)) for link in image]
                await asyncio.gather(*tasks)

        async def fetch(link, session):
            if not thumbnail:
                src = link.replace("/t.", "/i.").replace("t.", ".")
            async with session.get(src) as resp:
                while resp.status != 200:
                    if session.get(src).status == 200:
                        break

                if not thumbnail:
                    src_ = src.replace("https://i.nhentai.net/galleries/", "")
                else:
                    src_ = src.replace("t.",".").replace("https://.nhentai.net/galleries/", "")
                try:
                    chunk = await resp.content.read()
                    self.comic_set[src_] = base64.b64encode(chunk).decode("utf-8")
                except Exception as e:
                    print(f"{src}:{e}")
                    tasks.append(asyncio.create_task(fetch(link, session)))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main(image))
        loop.close()

        return self.comic_set

    def download(self,path_: str = "./", thumbnail: bool = False):
        """
        Download and save the image to local directory

        Args:
            path (str): Local directory
        """

        img = self.image()
        for i in img:
            a = i.replace("/", "-")
            if not path.exists(f"{path_}{self.code}"):
                makedirs(f"{path_}{self.code}")
            with open(f"{path_}{self.code}/{a}", "wb") as f:
                f.write(base64.b64decode(img[i]))
