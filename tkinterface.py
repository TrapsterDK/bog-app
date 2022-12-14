from decimal import Decimal
import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkinter import ttk
from typing import Any
from database import *
from tkinter import messagebox

# entry with placeholder
class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master, placeholder, sv = None, color='grey', **kwargs):
        if sv is None:
            sv = tk.StringVar()

        super().__init__(master, textvariable=sv, **kwargs)

        self.sv = sv
        self._placeholder_text = placeholder
        self._placeholder_color = color
        self._default_color = self['fg']

        self.bind("<FocusIn>", self._foc_in)
        self.bind("<FocusOut>", self._foc_out)

        self._foc_out()

    # delete placeholder on focus
    def _foc_in(self, *args) -> None:
        if self['fg'] != self._placeholder_color:
            return

        # deletion done first to prevent extra write callback
        self.delete(0, tk.END)
        self['fg'] = self._default_color

    # add placeholder if no text
    def _foc_out(self, *args)  -> None:
        if self.get():
            return

        # background set first to prevent wrong validation
        self['fg'] = self._placeholder_color
        self.insert(0, self._placeholder_text)

    # get value while preventing get placholder
    def get(self) -> str:
        if self['fg'] == self._placeholder_color:
            return None
        
        return self.sv.get()

    # set value while insuring proper placeholder
    def set(self, value: str) -> None:
        if value:
            self.delete(0, tk.END)
            self['fg'] = self._default_color
            self.insert(0, value)
            
            if self.get():
                return

            self['fg'] = self._placeholder_color
            self.insert(0, self._placeholder_text)

    # prevent write event to fire when it is just placeholder being written
    def _write_callback(self, *args) -> None:
        if self['fg'] == self._placeholder_color:
            return
        
        self._write_callback_original(args)

    # add trace callback
    def sv_trace_add(self, mode: Any, callback: Callable) -> str:
        if(mode == 'write'):
            self._write_callback_original = callback
            return self.sv.trace_add(mode, self._write_callback)
            
        return self.sv.trace_add(mode, callback)
    
    # set validation callback
    def validate(self, callback: Callable, validate_type) -> None:
        self._validate_callback = callback
        self._validate_type = validate_type
        self.configure(validate=tk.ALL, validatecommand=(self.register(self._validate), '%P'))

    # prevent validating when it is just placeholder being written
    def _validate(self, P: str) -> bool:
        if self['fg'] == self._placeholder_color:
            return True

        return self._validate_callback(P, self._validate_type)

class PopUp(tk.Toplevel):
    #close callback defaults to button1 callback, return true to close after callback
    def __init__(self, title, button_callback2, button_callback1=None, button_text2="Bekr??ft", button_text1="Annuller", size="300x155", close_callback=None, *args, **kwargs) -> None:
        if not close_callback:
            close_callback = button_callback1

        super().__init__(*args, **kwargs)

        #close
        self.protocol("WM_DELETE_WINDOW", lambda: self._callback(close_callback))

        # always top, non resizable, no maximize or minimize
        self.focus_force()
        self.attributes("-topmost", True)
        self.attributes('-toolwindow', True)
        self.resizable(False, False)
        self.grab_set()
        
        self.geometry(size)
        self.wm_title(title)

        bf = tk.Frame(self)

        b1 = ttk.Button(bf, text=button_text1, command=lambda: self._callback(button_callback1))
        b2 = ttk.Button(bf, text=button_text2, command=lambda: self._callback(button_callback2))
    
        bf.pack(side=tk.BOTTOM, fill=tk.X, expand=True, padx=2, pady=(0,2), anchor=tk.S) 
        b1.pack(side=tk.LEFT, fill=tk.X, expand=True)
        b2.pack(side=tk.LEFT, fill=tk.X, expand=True)
    

    def _callback(self, callback) -> None:
        if callback == None or callback(self):
            self.destroy()

class PopUpText(PopUp):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label = tk.Label(self, text=text, font=("Arial", 11), wraplength=280, anchor=tk.N)
        label.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(8, 0))

    

_MORE = 0
_EVEN = 1
_ODD = 2
_HIGHLIGHT = 3
_LATE = 0
_MORE_TEXT = -1
_MORE_VALUES = ("Inl??s flere b??ger", "-")
# table with alternating row colors, hover effect, heading sort by callback
class FancyTable(ttk.Treeview):
    def __init__(self, master, columns, load_more_callback: Callable, sort_by_callback: Callable, more_color = "#909090", even_row_color = "#DFDFDF", odd_row_color = "#ffffff", **kwargs):
        super().__init__(master, columns=columns, **kwargs)

        self.columns: list[str] = columns
        self._load_more_callback = load_more_callback

        # create headers
        for column in columns:
            # command on click of header call sort_by_callback
            self.heading(column, text=column, command = lambda c=column: sort_by_callback(c))
            self.column(column, width=1)

        #colors for tags
        self.tag_configure(_MORE, background= more_color)
        self.tag_configure(_EVEN, background= even_row_color)
        self.tag_configure(_ODD, background=  odd_row_color)
        self.tag_configure(_HIGHLIGHT, background='lightblue')

        # hover highlight
        self.add_bindtag(2, _LATE)
        self.bind_class(_LATE, "<MouseWheel>", self._hover_highlight)
        self.bind_class(_LATE, '<Enter>', self._hover_highlight)
        self.bind("<Motion>", self._hover_highlight)
        self.bind('<Leave>', self._hover_highlight)

        # load more
        self.bind("<<TreeviewSelect>>", self._select)
    
    # get color based on row index position in tree
    def _row_color_index(self, index: int) -> int:
        return (_EVEN if index%2==0 else _ODD)
        
    # set color based in iid
    def _set_row_color_iid(self, iid: int) -> int:
        if(self.item(iid)['text'] == _MORE_TEXT):
            self.item(iid, tags=(_MORE,))
        else:
            self.item(iid, tags=self._row_color_index(self.index(iid)))

    _prev_hover_iid = None
    # highligthing of rows on hover, misses by one on start
    def _hover_highlight(self, event: tk.Event) -> None:
        # if leave mouse, remove highlight
        if(event.type == tk.EventType.Leave):
            self._set_row_color_iid(self._prev_hover_iid)
            self._prev_hover_iid = None
            return

        iid = self.identify_row(event.y)

        if iid == self._prev_hover_iid:
            return
        
        # set color
        self.item(iid, tags=_HIGHLIGHT)

        # remove color from previous
        if self._prev_hover_iid and self.exists(self._prev_hover_iid):
            self._set_row_color_iid(self._prev_hover_iid)

        self._prev_hover_iid = iid

    # adds a bindtag at a given position
    def add_bindtag(self, pos: int, tag: Any) -> None:
        new_bind_tags = list(self.bindtags())
        new_bind_tags.insert(pos, tag)
        self.bindtags(new_bind_tags)

    # load more if selected more row
    def _select(self, *args) -> None:   
        selection = self.selection()
        if selection and self.item(selection[-1])['text'] == _MORE_TEXT:
            self._load_more_callback()

    # add list of rows, dont use insert
    def add_rows(self, text: list[str], values: list[tuple[Any, ...]], more: bool, delete_existing_rows: bool = False) -> None:
        if len(self.get_children()): 
            if delete_existing_rows: # remove all rows
                self.yview_moveto(0)
                self.delete(*self.get_children())
            else: # remove more row
                self.delete(self.get_children()[-1])

        index = len(self.get_children())

        # add rows
        for i, (t, v) in enumerate(zip(text, values)):
            self.insert('', index + i, values=v, text=t, tags=self._row_color_index(index + i))
        
        # load more
        if more:
            more_values = [_MORE_VALUES[0]] + [_MORE_VALUES[1]] * (len(values[0])-1)
            self.insert("", index + len(values), text=_MORE_TEXT, values=more_values, tags=(_MORE,))
        
        # check to see if refresh of highlight is needed
        if not self.winfo_ismapped():
            return

        self.event_generate("<Motion>",
            x=self.winfo_pointerx() - self.winfo_rootx(), 
            y=self.winfo_pointery() - self.winfo_rooty())
    
    # redraw rows color
    def redraw(self) -> None:
        for iid in self.get_children():
            if(self.item(iid)['text'] == _MORE_TEXT):
                self.item(iid, tags=(_MORE,))
            else:
                self.item(iid, tags=self._row_color_index(self.index(iid)))


#class for tkinter app
TITLE = "Bog butik"
class App(tk.Tk):
    none_item = "**Ukendt**"
    tree_load = 50

    columns =           ("Titel", "Forfatter", "Gruppe", "Produktkode")
    sort_by_options =   ["Titel A-Z", "Titel Z-A", "Forfatter A-Z", "Forfatter Z-A", "Group A-Z", "Group Z-A", "Produktkode stigende", "Produktkode faldende"]
    sort_by_values =    [sort_by.title_asc, sort_by.title_desc, sort_by.author_asc, sort_by.author_desc, sort_by.group_asc, sort_by.group_desc, sort_by.product_code_asc, sort_by.product_code_desc]

    data_text = ["Titel", "Forfattere", "Gruppe", "Produktkode", "Pris", "Antal", "Redakt??r", "Sider", "Forl??gger"]
    data = ["title", "authors", "group", "product_code", "price", "stock", "editor", "pages", "publisher"]
    data_type = [str, list, str, int, decimal.Decimal, int, str, int, str]

    def __init__(self, db_name="database.db"):
        super().__init__()

        self.db = Database(db_name)
        self.title(TITLE)
        self.geometry("800x600")

        self._create_widgets()

    def _create_widgets(self):
        self._left_frame = tk.Frame(self)
        self._left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self._right_frame = tk.Frame(self)
        self._right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0,6))

        self._buttons_frame = tk.Frame(self._left_frame)
        self._buttons_frame.pack(side=tk.LEFT, padx=4, fill = tk.Y)

        self._search_frame = tk.Frame(self._right_frame)
        self._search_frame.pack(side=tk.TOP, fill=tk.X, padx=(0, 17), pady=(0, 6)) # 17 chosen to make scrollbar fit
        self._tree_frame = tk.Frame(self._right_frame)
        self._tree_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self._search_top_frame = tk.Frame(self._search_frame)
        self._search_top_frame.pack(side=tk.TOP, fill=tk.X)
        self._search_bottom_frame = tk.Frame(self._search_frame)
        self._search_bottom_frame.pack(side=tk.BOTTOM, fill=tk.X) 

        self._search_top_left_frame = tk.Frame(self._search_top_frame)
        self._search_top_left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._search_top_right_frame = tk.Frame(self._search_top_frame)
        self._search_top_right_frame.pack(side=tk.RIGHT, fill=tk.X)

        # saldo label
        self._saldo_label = tk.Label(self._buttons_frame, text = "Saldo:", font = 'Helvetica 12 bold')
        self._saldo_label.pack(anchor = tk.N, side = tk.TOP, pady = (5,0))

        self._saldo_label_amount = tk.Label(self._buttons_frame, text = self.db.get_saldo(), font = 'Helvetica 12')
        self._saldo_label_amount.pack(anchor = tk.N, side = tk.TOP, pady = (0,30))

        #create button
        self._info_button = tk.Button(self._buttons_frame, text="Info", command=lambda: self._book_popup("Bog info", None, True, True), width=15)
        self._add_button = tk.Button(self._buttons_frame, text="Tilf??j", command=lambda: self._book_popup("Tilf??g bog", self._add_book, False, False), width=15)
        self._delete_button = tk.Button(self._buttons_frame, text="Slet", command=self._delete_book, width=15)
        self._update_button = tk.Button(self._buttons_frame, text="Rediger", command=lambda: self._book_popup("Rediger bog", self._edit_book, True, False), width=15)
        self._sell_button = tk.Button(self._buttons_frame, text="S??lg", command=self._sell_book, width=15)

        self._info_button.pack(pady=2, ipady = 11)
        self._add_button.pack(pady=2, ipady = 11)
        self._delete_button.pack(pady=2, ipady = 11)
        self._update_button.pack(pady=2, ipady = 11)
        self._sell_button.pack(pady=2, ipady = 11)

        #add search title
        search_title = tk.Label(self._search_top_left_frame, text="B??ger", font='Helvetica 15 bold')
        search_title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        #optionmenu text
        sort_by_label = tk.Label(self._search_top_right_frame, text="Sorter efter: ", font='Helvetica 12')
        sort_by_label.pack(side=tk.LEFT, fill=tk.X)

        self._create_sortmenu()
        self._create_searchbars()
        self._create_table()
        

    def _create_sortmenu(self):
        # variable for sort by option
        self.sort_by = tk.StringVar()
        self.sort_by.set(self.sort_by_options[0])   
        self.sort_by.trace_add("write", self._tree_set_rows)
        
        # menu
        sort_optionmenu = tk.OptionMenu(self._search_top_right_frame, self.sort_by, *self.sort_by_options)
        sort_optionmenu.config(width=25)
        sort_optionmenu.pack(side=tk.RIGHT, fill=tk.X)

    def _create_table(self):
        # create treeview
        self._tree = FancyTable(self._tree_frame, columns=self.columns, load_more_callback=self._tree_add_rows, sort_by_callback=self._tree_sort_by_coloumn, show='headings')
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH,  expand=True)

        # select rows 
        self._tree.bind("<<TreeviewSelect>>", self._tree_on_select, add="+")

        # create scrollbar for treeview
        vsb = ttk.Scrollbar(self._tree_frame, orient="vertical", command=self._tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree.configure(yscrollcommand=vsb.set)
        
        # refresh treeview
        self._tree_add_rows()
        self._tree_on_select()


    def _create_searchbars(self):
        # create search bar list
        self._search_bars = []

        # search bar for each coloumn
        for column in self.columns:
            search_bar = EntryWithPlaceholder(self._search_bottom_frame, "S??g " + column.lower(), width=1)
            search_bar.sv_trace_add("write", self._tree_set_rows)
            search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self._search_bars.append(search_bar)

        #allow only numbers for product code
        self._search_bars[3].validate(self._validate, int)

    @staticmethod   
    def _validate(P: str, vtype):
        try:
            if P == "" or vtype(P):
                return True
        except:
            pass
        return False

    def _info(self):
        pass

    def _book_from_popup(self, popup, book):
        for thing, entry, vtype in zip(self.data, popup.entries, self.data_type):
            value = entry.get()
            if value:
                if vtype == list:
                    value = map(str.strip, value.split(','))
                else:
                    value = vtype(value)

            setattr(book, thing, value)

        return book

    def _add_book(self, popup):
        book = self._book_from_popup(popup, Book())
        if book.title == None:
            messagebox.showerror("Fejl", "Bogen skal have en titel")
            return False

        self.db.add_book(book)
        self._tree_set_rows()
        return True
        
    def _edit_book(self, popup):
        book = self._book_from_popup(popup, self.book)
        if book.title == None:
            messagebox.showerror("Fejl", "Bogen skal have en titel")
            return False

        self.db.edit_book(book)
        self._tree_set_rows()
        return True

    def _book_popup(self, title, callback, book=False, label=False):
        popup = PopUp(title, callback, size=str(400) + "x" + str(len(self.data)*24+2))

        add_menu_vframe = tk.Frame(popup)
        add_menu_hframe = tk.Frame(popup)
        add_menu_vframe.pack(side=tk.LEFT, fill = tk.BOTH, expand = False)
        add_menu_hframe.pack(side=tk.LEFT, fill = tk.BOTH, expand = True)

        popup.entries = []

        e_font  = font.nametofont("TkDefaultFont")

        for thing, thing_text, thing_type in zip(self.data, self.data_text, self.data_type):
            titel_label = tk.Label(add_menu_vframe, text = thing_text + ": ")  
            titel_label.pack(side = tk.TOP, anchor=tk.NW)

            if book:
                book = self.db.get_book(self._tree.item(self._tree.selection()[0])['text'])

                attr = getattr(book, thing)
                if attr == None:
                    text = None
                elif thing_type == list:
                    text = ', '.join(attr)
                else:
                    text = attr

            if label:
                if len(str(text)) > 48:
                    text = str(text)[:48] + "..."
                entry = tk.Label(add_menu_hframe, text=text, anchor=tk.W)
                entry.pack(side = tk.TOP, fill=tk.X, expand=True)
            else:
                if thing_type == list:
                    example = "(f.eks. 'Hans, Jens Peter')"
                elif thing_type == int:
                    example = "(f.eks. '123')"
                elif thing_type == decimal.Decimal:
                    example = "(f.eks. '123.45' eller '123')"
                else:
                    example = "(f.eks. 'Fantasy')"

                placeholder = f"Skriv {thing_text.lower()}"
                placeholder_first_len = e_font.measure(placeholder)
                space_len = e_font.measure(" ")
                placeholder += f"{' ' * int(40 - placeholder_first_len/space_len)}{example}"

                entry = EntryWithPlaceholder(add_menu_hframe, placeholder)
                entry.validate(self._validate, thing_type)

                if book:
                    self.book = book
                    entry.set(text)
                    
                entry.pack(side = tk.TOP, fill=tk.X, expand=True, pady = 1)

            popup.entries.append(entry)
                    

    def _delete_book(self):
        #delete from database
        ids = [self._tree.item(selection)['text'] for selection in self._tree.selection()]
        self.db.delete_books(ids)

        # delete from tree
        self._tree.delete(*self._tree.selection())

        # refresh treeview
        self._tree.redraw()
        pass

    def _sell_book(self):
        book = self.db.get_book(self._tree.item(self._tree.selection()[0])['text'])
        
        if 50 < len(book.title):
            book.title = book.title[:80] + "..."

        if(0 < book.stock):
            PopUpText(f'S??lg bogen:\n"{book.title}"\nPris: {book.price}kr\nLager: {book.stock}', "S??lg", self._sell_book_accept)
        else:
            PopUpText(f'Bogen \n"{book.title}"\n Er udsolgt', "S??lg", None, button_callback1=None, button_text2="Tilbage", button_text1=None)

    def _sell_book_accept(self, popup):
        transaction = Transaction(
            book_id = self._tree.item(self._tree.selection()[0])['text'],
            quantity = 1
        )
        
        self.db.sell_book(transaction)
        self._saldo_label_amount.configure(text = self.db.get_saldo())
        return True

    # sort by coloumn callback when tree header is clicked, set sort_by optionmenu to the clicked coloumn
    def _tree_sort_by_coloumn(self, coloumn: str) -> None:
        column_index = self.columns.index(coloumn)*2
        optionmenu_index = self.sort_by_options.index(self.sort_by.get())

        value = self.sort_by_options[column_index+1 if column_index == optionmenu_index else column_index]

        self.sort_by.set(value)   

    def _tree_on_select(self, *args) -> None:
        selection = self._tree.selection()
        
        #button disable enable
        match len(selection):
            case 0:
                self._info_button['state'] = tk.DISABLED
                self._add_button['state'] = tk.NORMAL
                self._delete_button['state'] = tk.DISABLED
                self._update_button['state'] = tk.DISABLED
                self._sell_button['state'] = tk.DISABLED
            case 1:
                self._info_button['state'] = tk.NORMAL
                self._add_button['state'] = tk.NORMAL
                self._delete_button['state'] = tk.NORMAL
                self._update_button['state'] = tk.NORMAL
                self._sell_button['state'] = tk.NORMAL
            case _:
                self._info_button['state'] = tk.DISABLED
                self._add_button['state'] = tk.NORMAL
                self._delete_button['state'] = tk.NORMAL
                self._update_button['state'] = tk.DISABLED
                self._sell_button['state'] = tk.DISABLED

    # delete current rows and add new ones
    def _tree_set_rows(self, *args) -> None:
        self._tree_add_rows(True)

    # adds rows to tree with choice to delete current rows
    def _tree_add_rows(self, delete_children: bool = False) -> None:
        # search query
        search = Book_Search_Query(
            title=self._search_bars[0].get() or None, 
            author=self._search_bars[1].get() or None, 
            group=self._search_bars[2].get() or None, 
            product_code=self._search_bars[3].get() or None)

        # sql query
        books = self.db.get_minbooks(   
            search, 
            self.sort_by_values[self.sort_by_options.index(self.sort_by.get())], 
            limit=self.tree_load+1, 
            offset=0 if delete_children else len(self._tree.get_children())-1)

        # check if are more books to load
        more_books = len(books) > self.tree_load

        # remove last book as we loaded one to much to detect if there are more books
        if more_books:
            books = books[:-1]

        # add to tree
        self._tree.add_rows(
            text = [book.id for book in books], 
            values = ( [(book.title or self.none_item, ', '.join(book.authors) if book.authors else self.none_item, 
                        book.group or self.none_item, book.product_code or self.none_item)
                        for book in books]),
            more = more_books,
            delete_existing_rows = delete_children)


if __name__ == "__main__":
    app = App()
    app.mainloop()