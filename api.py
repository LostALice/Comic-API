# Code by AkinoAlice@Tyrant_Rex

import requests, aiohttp, asyncio, base64
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from os import path,makedirs

class nhentai:
    def __init__(self):
        self.code = None
        self.info = None
        self.title = None
        self.sub_title = None
        self.parodies = None
        self.tag = None
        self.artists = None
        self.groups = None
        self.languages = None
        self.categories = None
        self.pages = None
        self.uploaded = None
        self.popular = None
        self.comics = None

    def infos(self, code: int = None):
        """
        Get the doujinshi information from nhentai.net

        Args:
            code (int): /g/<code>

        self.info = All information

        {
            "title" " "Title"
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

        try:
            self.code = int(code)
        except Exception as e:
            print(e)
            raise BaseException("Code incorrect")

        ua = UserAgent()
        header = {'user-agent': ua.random}
        html = requests.get(f"https://nhentai.net/g/{code}/",headers=header)
        if html.status_code == 404:
            raise BaseException("404 Not Found")

        soup = BeautifulSoup(html.text, "lxml")
        page = soup.find_all(class_="tag-container field-name")

        json = {"Code": code}
        json["Title"] = [item.text for item in soup.find_all("h1", attrs={"class": "title"})[0]]

        try:
            json["Sub_Title"] = [item.text for item in soup.find_all("h2", attrs={"class": "title"})[0]]
        except:
            json["Sub_Title"] = None

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

        info_staff = ["Parodies","Tags","Artists","Groups","Languages","Categories","Pages","Uploaded","Sub_Title","Title"]
        for staff in info_staff:
            if not staff in json: json[staff] = None

        self.info = json
        self.title = json["Title"]
        self.sub_title = json["Sub_Title"]
        self.parodies = json["Parodies"]
        self.tag = json["Tags"]
        self.artists = json["Artists"]
        self.groups = json["Groups"]
        self.languages = json["Languages"]
        self.categories = json["Categories"]
        self.pages = json["Pages"]
        self.uploaded = json["Uploaded"]

        return self.info

    def image(self,code: int = None, thumbnail: bool = False):
        self.comics = {}
        """
        Get the doujinshi base64 encoded string from nhentai.net

        Returns:
           self.comics: {"path":"<base64 string>"}
        """

        if code == None:
            try:
                self.code = int(code)
            except Exception as e:
                print(e)
                raise BaseException("Code incorrect")


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
                    self.comics[src_] = base64.b64encode(chunk).decode("utf-8")
                except Exception as e:
                    print(f"{src}:{e}")
                    tasks.append(asyncio.create_task(fetch(link, session)))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main(image))
        loop.close()

        return self.comics

    def download(self,code: int = None, path_: str = "./", thumbnail: bool = False):
        """
        Download and save the image to local directory

        Args:
            path (str): Local directory
        """

        if code == None:
            try:
                self.code = int(code)
            except Exception as e:
                print(e)
                raise BaseException("Code incorrect")

        img = self.image(code)
        for i in img:
            a = i.replace("/", "-")
            if not path_.endswith("/"): path_ += "/"
            if not path.exists(f"{path_}{self.code}"): makedirs(f"{path_}{self.code}")

            with open(f"{path_}{self.code}/{a}", "wb") as f:
                f.write(base64.b64decode(img[i]))

    def popular_now(self) -> list:
        """
        Get todays popular doujinshi

        Returns:
            list: self.popular
        """

        soup = BeautifulSoup(requests.get("https://nhentai.net").text, "lxml")
        page = [p for p in soup.find_all("a", attrs={"class": "cover"})[:5]]
        self.popular = [p.attrs["href"].replace("/","").replace("g","") for p in page]
        return self.popular

    def latest(self) -> int:
        """
        Get the latest doujinshi

        Returns:
            int: self.latest
        """

        soup = BeautifulSoup(requests.get("https://nhentai.net").text, "lxml")
        page = soup.find_all("a", attrs={"class": "cover"})[5]
        self.latest = int(page.attrs["href"].replace("/","").replace("g",""))
        return self.latest
