'''Card Catalog of the Great Library of Peercoin
https://en.wikipedia.org/wiki/Library_catalog
'''

from kivy.app import App
from kivy.uix.button import Button

class CardCatalogApp(App):
    def build(self):
        return Button(text='I wanna be a library when I grow up!')

CardCatalogApp().run()
