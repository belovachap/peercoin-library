"""The Great Library of Peercoin
https://en.wikipedia.org/wiki/Library
https://en.wikipedia.org/wiki/Library_catalog
"""

from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.textinput import TextInput


BOOKS = [
    {
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "txid": "3154d03bcc1f8fbfd89f2c3672567791187c95ba97d55ca05eca2ab4f40c3430",
    },
]


class CardCatalog(ListView):

    def __init__(self, *args, **kwargs):
        super(CardCatalog, self).__init__(*args, **kwargs)

        def args_converter(row_index, book):
            return {
                "text": book["title"],
                "size_hint_y": None,
                "height": 25,
            }

        list_adapter = ListAdapter(
            data=BOOKS,
            args_converter=args_converter,
            cls=ListItemButton,
            selection_mode="single",
        )

        self.adapter = list_adapter


class MediaViewer(TextInput):

    PLEASE_SELECT_MESSAGE = "Please select a book from the card catalog."

    def __init__(self, *args, **kwargs):
        super(MediaViewer, self).__init__(*args, **kwargs)
        self.text = self.PLEASE_SELECT_MESSAGE

    def book_changed(self, list_adapter):

        if len(list_adapter.selection) == 0:
            self.text = self.PLEASE_SELECT_MESSAGE
            return

        book = BOOKS[list_adapter.selection[0].index]
        self.text = "{0}\nby {1}\nin tx {2}".format(book["title"], book["author"], book["txid"])


class LibraryBrowser(BoxLayout):

    card_catalog = ObjectProperty()
    media_viewer = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(LibraryBrowser, self).__init__(*args, **kwargs)

        self.card_catalog.adapter.bind(
            on_selection_change=self.media_viewer.book_changed
        )


class LibraryApp(App):

    def build(self):
        return LibraryBrowser()


if __name__ == "__main__":
    LibraryApp().run()
