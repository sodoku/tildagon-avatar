import os
import sys

import app
import requests
import settings
from app_components import Notification, clear_background
from events.input import BUTTON_TYPES, Buttons

if sys.implementation.name == "micropython":
    apps = os.listdir("/apps")
    path = ""
    for a in apps:
        if a == "sodoku_tildagon_avatar":
            path = "/apps/" + a
    ASSET_PATH = path + "/assets/"
else:
    ASSET_PATH = "apps/avatar/assets/"


def file_exists(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) == 0
    except OSError:
        return False


class Avatar(app.App):
    def __init__(self):
        self.notification = None
        self.button_states = Buttons(self)
        self.name = settings.get("name") or "emfcamp"
        self.image_path = ASSET_PATH + self.name + ".png"
        self.url = "https://github.com/" + self.name + ".png?size=240"
        self.image_exists = False

    def update(self, delta):
        if file_exists(self.image_path):
            self.image_exists = True
        else:
            self.image_exists = False

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()
        if self.button_states.get(BUTTON_TYPES["CONFIRM"]):
            self.download_avatar()

        if self.notification:
            self.notification.update(delta)

    def draw(self, ctx):
        if self.image_exists:
            clear_background(ctx)
            ctx.save()
            ctx.image(self.image_path, -120, -120, 240, 240)
            ctx.restore()
        else:
            ctx.save()
            ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()
            ctx.font_size = 18
            ctx.rgb(1, 0, 0).move_to(-80, 0).text("No avatar found")
            ctx.font_size = 14
            ctx.rgb(1, 0, 0).move_to(-80, 20).text("Press CONFIRM to download")
            ctx.rgb(1, 0, 0).move_to(-80, 40).text("Github username: " + self.name)
            ctx.restore()

        if self.notification:
            self.notification.draw(ctx)

    def download_avatar(self):
        print("Downloading " + self.url)
        response = requests.get(self.url)
        if response.status_code == 200:
            with open(self.image_path, "wb") as file:
                file.write(response.content)
                print("Sucessfully downloaded " + self.url)
        else:
            self.notification = Notification("Failed")
            print("Could not download " + self.url)


__app_export__ = Avatar
