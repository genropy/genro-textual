"""
Tutorial Textual+Bag #01 - Hello World

Stessa app di tutorial_textual/01_hello_world.py
ma costruita con BagApp.

Esegui con: python 01_hello_world.py
"""

from genro_textual import TextualApp


class MyApp(BagApp):
    def build(self):
        self.page.static("Hello, Textual!")
        self.page.static("Built with BagApp")


if __name__ == "__main__":
    MyApp().run()
