"""The Great Library of Peercoin
https://en.wikipedia.org/wiki/Library
https://en.wikipedia.org/wiki/Library_catalog
"""

import codecs

from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.textinput import TextInput

from peercoin import call_peercoin_rpc


HEX_DECODER = codecs.getdecoder("hex_codec")

BOOKS = [
    {
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "transaction_id": "3154d03bcc1f8fbfd89f2c3672567791187c95ba97d55ca05eca2ab4f40c3430",
    },
    {
        "title": "Romeo and Juliet",
        "author": "William Shakespeare",
        "transaction_id": "f40b4c7e97f2e83d1923481c19aed2f6ccaee470c636f7857dc4c970113df204",
    },
    {
        "title": "Through the Looking-Glass",
        "author": "Lewis Carroll",
        "transaction_id": "0a440999bafedbdf0e3bdc52f6bdb8caf9634cb38cfef84c8fc2a8ad3f853059",
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


def get_book_text_at_transaction_id(transaction_id):
    '''Returns a string of the book text stored at the passed transaction id.

    Raises NoBookFoundError if a book cannot be extracted.
    '''
    result = call_peercoin_rpc('getrawtransaction', transaction_id)

    return HEX_DECODER(result)[0]


class MediaViewer(TextInput):

    PLEASE_SELECT_MESSAGE = "Please select a book from the card catalog."

    def __init__(self, *args, **kwargs):
        super(MediaViewer, self).__init__(*args, **kwargs)
        self.text = self.PLEASE_SELECT_MESSAGE

    def book_changed(self, list_adapter):
        'Updates Media Veiwer with selected book details and text.'
        if len(list_adapter.selection) == 0:
            self.text = self.PLEASE_SELECT_MESSAGE
            return

        book = BOOKS[list_adapter.selection[0].index]
        self.text = "{0}\nby {1}\nin peercoin transaction {2}\n\n{3}".format(
            book["title"],
            book["author"],
            book["transaction_id"],
            get_book_text_at_transaction_id(book["transaction_id"])
        )
        self.cursor = (0, 0) # Scroll back to the top of the text box


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
