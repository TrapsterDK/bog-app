from time import sleep
import tkinter as tk
from tkinter import ttk
from database import *

# entry with placeholder, and proper get and write callbacks
class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master, placeholder, textvariable = None, color='grey', **kwargs):
        if textvariable is None:
            self.textvariable = tk.StringVar()
        else:
            self.textvariable = textvariable

        super().__init__(master, textvariable=self.textvariable, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_color = self['fg']

        self.bind("<FocusIn>", self._foc_in)
        self.bind("<FocusOut>", self._foc_out)

        self._foc_out()

    def _foc_in(self, *args):
        if self['fg'] != self.placeholder_color:
            return

        self.delete(0, tk.END)
        self['fg'] = self.default_color

    def _foc_out(self, *args):
        if self.get():
            return

        self['fg'] = self.placeholder_color
        self.textvariable.set(self.placeholder)

    def get(self):
        if self['fg'] == self.placeholder_color:
            return None
        
        return self.textvariable.get()

    def _write_callback(self, *args):
        print(args)
        if self['fg'] == self.placeholder_color:
            return
        
        self.write_callback_original(args)

    def trace_add(self, mode, callback):
        if(mode == 'write'):
            self.write_callback_original = callback
            return self.textvariable.trace_add(mode, self._write_callback)
            
        return self.textvariable.trace_add(mode, callback)


#class for tkinter app
class App(tk.Tk):
    none_item = "**Ukendt**"
    more_text = -1
    tree_load = 50
    #sort by option
    sort_by_options =       ["Titel A-Z", "Titel Z-A", "Forfatter A-Z", "Forfatter Z-A", "Genre A-Z", "Genre Z-A", "Produktkode stigende", "Produktkode faldende"]
    columns =               ("Titel", "Forfatter", "Genre", "Produktkode")
    sort_by_to_options =    [sort_by.title_asc, sort_by.title_desc, sort_by.author_asc, sort_by.author_desc, sort_by.genre_asc, sort_by.genre_desc, sort_by.product_code_asc, sort_by.product_code_desc]

    def __init__(self, db_name="database.db"):
        super().__init__()
        self.db = Database(db_name)
        self.title("Bog butik")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx= (8,0), pady=(0,7))

        self.search_frame = tk.Frame(self.right_frame)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=(0, 17), pady=(0, 6)) # 17 chosen to make scrollbar fit
        self.tree_frame = tk.Frame(self.right_frame)
        self.tree_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.search_top_frame = tk.Frame(self.search_frame)
        self.search_top_frame.pack(side=tk.TOP, fill=tk.X)
        self.search_bottom_frame = tk.Frame(self.search_frame)
        self.search_bottom_frame.pack(side=tk.BOTTOM, fill=tk.X) 

        self.search_top_left_frame = tk.Frame(self.search_top_frame)
        self.search_top_left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_top_right_frame = tk.Frame(self.search_top_frame)
        self.search_top_right_frame.pack(side=tk.RIGHT, fill=tk.X)


        #create button
        self.info_button = tk.Button(self.left_frame, text="Info", command=self.info)
        self.add_button = tk.Button(self.left_frame, text="Tilføj", command=self.add_book)
        self.delete_button = tk.Button(self.left_frame, text="Slet", command=self.delete_book)
        self.update_button = tk.Button(self.left_frame, text="Opdater", command=self.update_book)

        self.info_button.pack()
        self.add_button.pack()
        self.delete_button.pack()
        self.update_button.pack()

        #create treeview
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings', name='tree')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH,  expand=True)

        #colors for tags
        self.tree.tag_configure("more", background="#B3B3B3")
        self.tree.tag_configure("#f2f", background="#f2f2f2")
        self.tree.tag_configure("#fff", background="#ffffff")

        self.tree.tag_configure('highlight', background='lightblue')
        self.tree.bind("<Motion>", self.highlight_row)

        #get late event after has treeview has scrollled and enter
        self.tree_add_bindtag(2, "Late")
        self.tree.bind_class("Late", "<MouseWheel>", self.highlight_row)
        self.tree.bind_class("Late", '<Enter>', self.highlight_row)

        self.tree.bind('<Leave>', self.highlight_row)

        #input 
        self.tree.bind("<<TreeviewSelect>>", self.tree_select)

        #create scrollbar
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.configure(yscrollcommand=vsb.set)

        #create search bar list
        self.search_bars = []

        #create columns
        for column in self.columns:
            self.tree.heading(column, text=column, command = lambda c=column: self.tree_sort_by(c))
            self.tree.column(column, width=1)
            
            search_bar = EntryWithPlaceholder(self.search_bottom_frame, "Søg " + column.lower(), width=1)
            search_bar.trace_add("write", self.tree_search)
            search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.search_bars.append(search_bar)

        #allow only numbers for product code
        self.search_bars[3].configure(validate=tk.ALL, validatecommand=((self.register(self._entry_restrict_numbers)), '%P'))

        #variable for sort by option
        self.sort_by = tk.StringVar()
        self.sort_by.set(self.sort_by_options[0])   
        self.sort_by.trace_add("write", self.tree_search)
        
        #menu
        sort_optionmenu = tk.OptionMenu(self.search_top_right_frame, self.sort_by, *self.sort_by_options)
        sort_optionmenu.config(width=25)
        sort_optionmenu.pack(side=tk.RIGHT, fill=tk.X)

        #add search title
        search_title = tk.Label(self.search_top_left_frame, text="Bøger", font='Helvetica 15 bold')
        search_title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        #optionmenu text
        sort_by_label = tk.Label(self.search_top_right_frame, text="Sorter efter: ", font='Helvetica 12')
        sort_by_label.pack(side=tk.LEFT, fill=tk.X)

        self.tree_select()
        self.tree_add()

    def _entry_restrict_numbers(self, P):
        print(P)
        if P.isdigit() or P == "":
            return True
        else:
            return False

    def info(self):
        pass

    def add_book(self):
        pass

    def delete_book(self):
        pass

    def update_book(self):
        pass

    def tree_add_bindtag(self, pos, tag):
        new_bind_tags = list(self.tree.bindtags())
        new_bind_tags.insert(pos, tag)
        self.tree.bindtags(new_bind_tags)
        
    #misses by one on start
    prev_hover_iid = None
    def highlight_row(self, event):
        print(event)
        tree = event.widget

        if(event.type == tk.EventType.Leave):
            tree.item(self.prev_hover_iid, tags=self._line_color(tree.index(self.prev_hover_iid)))
            self.prev_hover_iid = None
            return

        iid = tree.identify_row(event.y)

        if iid == self.prev_hover_iid:
            return
        
        tree.item(iid, tags="highlight")

        if self.prev_hover_iid and tree.exists(self.prev_hover_iid):
            tree.item(self.prev_hover_iid, tags=self._line_color(tree.index(self.prev_hover_iid)))

        self.prev_hover_iid = iid

    def tree_sort_by(self, column):
        column_index = self.columns.index(column)*2
        
        if (self.sort_by_options[column_index] == self.sort_by.get()):
            self.sort_by.set(self.sort_by_options[column_index + 1])
            return

        self.sort_by.set(self.sort_by_options[column_index])

    def tree_select(self, *args):
        selection = self.tree.selection()
        if selection and self.tree.item(selection[-1])['text'] == self.more_text:
            self.tree_add()
        
        #button disable enable
        match len(selection):
            case 0:
                self.info_button['state'] = tk.DISABLED
                self.add_button['state'] = tk.NORMAL
                self.delete_button['state'] = tk.DISABLED
                self.update_button['state'] = tk.DISABLED
            case 1:
                self.info_button['state'] = tk.NORMAL
                self.add_button['state'] = tk.NORMAL
                self.delete_button['state'] = tk.NORMAL
                self.update_button['state'] = tk.NORMAL
            case _:
                self.info_button['state'] = tk.DISABLED
                self.add_button['state'] = tk.NORMAL
                self.delete_button['state'] = tk.NORMAL
                self.update_button['state'] = tk.DISABLED
        
    def tree_add(self, *args):
        children = self.tree.get_children()

        if children:
            self.tree.delete(children[-1])

        self.tree_populate()

    def tree_search(self, *args):
        self.tree.delete(*self.tree.get_children())
        self.tree.yview_moveto(0)
        self.tree_populate()

    def _line_color(self, index):
        if (index == len(self.tree.get_children()) - 1):
            return ("more", )
        return ("#f2f" if index%2==0 else "#fff", )

    def tree_populate(self):
        search = Book_Search_Query(
            title=self.search_bars[0].get() or None, 
            author=self.search_bars[1].get() or None, 
            genre=self.search_bars[2].get() or None, 
            product_code=self.search_bars[3].get() or None)

        for i, book in enumerate(
            self.db.get_minbooks(   
                search, 
                self.sort_by_to_options[self.sort_by_options.index(self.sort_by.get())], 
                limit=self.tree_load, offset=len(self.tree.get_children())), 
            start=len(self.tree.get_children()) + 1):

            self.tree.insert("", tk.END, text = book.id, values = (book.title or self.none_item, book.author or self.none_item, book.genre or self.none_item, book.product_code or self.none_item), tags=(self._line_color(i), ))

        self.tree.insert("", tk.END, text=self.more_text,  value=("Inlæs flere bøger", "-", "-", "-"), tags=("more", ))
        
        # use x and y coordinates based on self.tree mouse position
        if self.tree.winfo_ismapped():
            self.tree.event_generate("<Motion>",
                x=self.tree.winfo_pointerx() - self.tree.winfo_rootx(), 
                y=self.tree.winfo_pointery() - self.tree.winfo_rooty())


if __name__ == "__main__":
    app = App()
    app.mainloop()