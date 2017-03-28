"""The Great Library of Peercoin
https://en.wikipedia.org/wiki/Library
https://en.wikipedia.org/wiki/Library_catalog
"""

import codecs
from gzip import GzipFile
import io
from os.path import expanduser

from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput

from peercoin import call_peercoin_rpc


HEX_DECODER = codecs.getdecoder("hex_codec")

BOOKS = [
    {
        "title": "Alice's Adventures in Wonderland",
        "authors": ["Lewis Carroll"],
        "transaction_id": "3154d03bcc1f8fbfd89f2c3672567791187c95ba97d55ca05eca2ab4f40c3430",
        "gzipped": False,
        "hex_left_trim": 9,
        "file_type": "txt",
    },
    {
        "title": "The Narrative of the Life of Frederick Douglass",
        "authors": ["Frederick Douglass"],
        "transaction_id": "7c126ee20c5cdc4c8717fe00aa953c402c19b0e3b8a4adac5b848723960a2e4e",
        "gzipped": False,
        "hex_left_trim": 9,
        "file_type": "txt",
    },
    {
        "title": "Romeo and Juliet",
        "authors": ["William Shakespeare"],
        "transaction_id": "f40b4c7e97f2e83d1923481c19aed2f6ccaee470c636f7857dc4c970113df204",
        "gzipped": False,
        "hex_left_trim": 9,
        "file_type": "txt",
    },
    {
        "title": "Through the Looking-Glass",
        "authors": ["Lewis Carroll"],
        "transaction_id": "0a440999bafedbdf0e3bdc52f6bdb8caf9634cb38cfef84c8fc2a8ad3f853059",
        "gzipped": False,
        "hex_left_trim": 6,
        "file_type": "txt",
    },
    {
        "title": "The Emancipation Proclamation",
        "authors": ["Abraham Lincoln"],
        "transaction_id": "2243568d8b9a92d4235503431bc0d2e0c1dfea049f906b66087ab589769fead6",
        "gzipped": True,
        "hex_left_trim": 4,
        "file_type": "txt",
    },
    {
        "title": "Peercoin White Paper",
        "authors": [
            "Sunny King",
            "Scott Nadal",
        ],
        "transaction_id": "1ff7ac2a0d2a87c846fefd57b8b4e8c3fb8ea1ee1d3c7fc9496c7dc407d9f622",
        "gzipped": False,
        "hex_left_trim": 9,
        "file_type": "pdf",
    },
    {
        "title": "The Declaration of Independence",
        "authors": ["Representatives of the United States of America"],
        "transaction_id": "6d852d9c3d7208233aa5906f155a602c02f9a0325786b45220cdc919a52eeb9d",
        "gzipped": True,
        "hex_left_trim": 4,
        "file_type": "txt",
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


class MediaScreenManager(ScreenManager):

    pdf_screen = ObjectProperty()
    text_screen = ObjectProperty()

    def media_changed(self, list_adapter):
        if len(list_adapter.selection) == 0:
            self.current = self.text_screen.name
            self.text_screen.text_widget.text = "Welcome to the Library!"
            return

        book = BOOKS[list_adapter.selection[0].index]

        if book["file_type"] == "pdf":
            self.current = self.pdf_screen.name
            self.pdf_screen.filename.text = self.pdf_screen.homedir
            self.pdf_screen.book = book
        else:
            self.current = self.text_screen.name
            tw = self.text_screen.text_widget
            tw.text = "{0}\nby {1}\nin peercoin transaction {2}\n\n{3}".format(
                book["title"],
                ", ".join(book["authors"]),
                book["transaction_id"],
                get_book_text_at_transaction_id(
                    book["transaction_id"],
                    book["gzipped"],
                    book["hex_left_trim"],
                )
            )
            tw.cursor = (0, 0) # Scroll back to the top of the text box


class PDFScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(PDFScreen, self).__init__(*args, **kwargs)
        self.homedir = expanduser("~")

    def save(self, filename):
        data = get_book_text_at_transaction_id(
            self.book["transaction_id"],
            self.book["gzipped"],
            self.book["hex_left_trim"],
        )

        with open(filename, 'wb') as pdf_file:
            pdf_file.write(data)


class TextScreen(Screen):
    pass


class LibraryBrowser(BoxLayout):

    card_catalog = ObjectProperty()
    media_screen_manager = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(LibraryBrowser, self).__init__(*args, **kwargs)

        self.card_catalog.adapter.bind(
            on_selection_change=self.media_screen_manager.media_changed
        )


class LibraryApp(App):

    def build(self):
        return LibraryBrowser()


if __name__ == "__main__":
    LibraryApp().run()
