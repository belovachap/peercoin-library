"""The Great Library of Peercoin
https://en.wikipedia.org/wiki/Library
https://en.wikipedia.org/wiki/Library_catalog
"""

import codecs
from gzip import GzipFile
import io

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
        "gzipped": False,
        "hex_left_trim": 9,
    },
    {
        "title": "The Narrative of the Life of Frederick Douglass",
        "author": "Frederick Douglass",
        "transaction_id": "7c126ee20c5cdc4c8717fe00aa953c402c19b0e3b8a4adac5b848723960a2e4e",
        "gzipped": False,
        "hex_left_trim": 9,
    },
    {
        "title": "Romeo and Juliet",
        "author": "William Shakespeare",
        "transaction_id": "f40b4c7e97f2e83d1923481c19aed2f6ccaee470c636f7857dc4c970113df204",
        "gzipped": False,
        "hex_left_trim": 9,
    },
    {
        "title": "Through the Looking-Glass",
        "author": "Lewis Carroll",
        "transaction_id": "0a440999bafedbdf0e3bdc52f6bdb8caf9634cb38cfef84c8fc2a8ad3f853059",
        "gzipped": False,
        "hex_left_trim": 6,
    },
    {
        "title": "The Emancipation Proclamation",
        "author": "Abraham Lincoln",
        "transaction_id": "2243568d8b9a92d4235503431bc0d2e0c1dfea049f906b66087ab589769fead6",
        "gzipped": True,
        "hex_left_trim": 4,
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


def get_book_text_at_transaction_id(transaction_id, gzipped, hex_left_trim):
    '''Returns a string of the book text stored at the passed transaction id.

    Raises NoBookFoundError if a book cannot be extracted.
    '''
    rawtransaction = call_peercoin_rpc('getrawtransaction', transaction_id)
    transaction = call_peercoin_rpc('decoderawtransaction', rawtransaction)

    book_data = None
    for vout in transaction['vout']:
        value = vout['value']
        script_asm = vout['scriptPubKey']['asm']
        script_hex = vout['scriptPubKey']['hex']

        if value == 0.0 and script_asm.startswith('OP_RETURN'):
            book_data = HEX_DECODER(script_hex)[0][hex_left_trim:]

    if book_data is None:
        raise NoBookFoundError()

    if gzipped:
        fileobj = io.BytesIO(book_data)
        book_data = GzipFile("", "rb", fileobj=fileobj).read()

    return book_data


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
            get_book_text_at_transaction_id(
                book["transaction_id"],
                book["gzipped"],
                book["hex_left_trim"],
            )
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
