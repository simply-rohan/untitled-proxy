# COntent AGgergator
from flask import *
from bs4 import BeautifulSoup, Tag
import requests
import urllib.parse

app = Flask(__name__)

proxy_url = "127.0.0.1"

file_type_lookup = {
    "jpeg": "image/jpeg",
    "jpg": "image",
    "png": "image",
    "css": "text/css",
    "html": "text/html",
    "js": "text/javascript",
    "ico": "image/ico",
    "svg": "image/svg",
    "gif": "image/gif"
}


def format_url(url):
    return "http://" + url.lstrip("https://").lstrip("http://")


def reroute(element: Tag, requested_url):

    def reference_type(ref: str):
        if ref.startswith("http"):
            return "global"
        elif ref.startswith("/"):
            return "local"
        else:
            return "unsupported"

    if element.name == "a":
        url = element.get("href")
        if url:
            ref_type = reference_type(url)
            if ref_type == "global":
                element["href"] = proxy_url + "render?url=" + url
            elif ref_type == "local":
                hostname = urllib.parse.urlparse(requested_url).netloc

                element["href"] = proxy_url + "render?url=" + hostname + url

    elif element.name == "link":
        url = element.get("href")
        if url:
            ref_type = reference_type(url)
            if ref_type == "global":
                element["href"] = proxy_url + "_load?url=" + url
            elif ref_type == "local":
                hostname = urllib.parse.urlparse(requested_url).netloc

                element["href"] = proxy_url + "_load?url=" + hostname + url

    elif element.name == "img":
        url = element.get("src")
        if url:
            ref_type = reference_type(url)
            if ref_type == "global":
                element["src"] = proxy_url + "_load?url=" + url
            elif ref_type == "local":
                hostname = urllib.parse.urlparse(requested_url).netloc
                print(proxy_url + "_load?url=" + hostname + url)

                element["src"] = proxy_url + "_load?url=" + hostname + url

    elif element.name == "script":
        url = element.get("src")
        if url:
            ref_type = reference_type(url)
            if ref_type == "global":
                element["src"] = proxy_url + "_load?url=" + url
            elif ref_type == "local":
                hostname = urllib.parse.urlparse(requested_url).netloc

                element["src"] = proxy_url + "_load?url=" + hostname + url


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/render")
def render():
    f_url = format_url(request.args.get("url"))
    page = requests.get(f_url)

    soup = BeautifulSoup(page.content)

    # Handle anchor tags
    for child in soup.descendants:
        reroute(child, f_url)

    return str(soup)


@app.route("/_load")
def _load():
    url = format_url(request.args.get("url"))
    cont = requests.get(url).content
    response = make_response(cont)

    response.headers.set("Content-Type", file_type_lookup[url.split(".")[-1]])
    response.headers.set("Content-Disposition", "attachment")
    return response
