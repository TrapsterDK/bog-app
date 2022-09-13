import tkinter as tk
from tkinter import Scrollbar, ttk
from turtle import width
from database import *

#class for tkinter app
class App(tk.Tk):
    none_item = "**Ukendt**"

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
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx= (10,0), pady=(0,7))

        self.search_frame = tk.Frame(self.right_frame)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=(0, 17), pady=(0, 6)) # 17 chosen to make scrollbar fit
        self.tree_frame = tk.Frame(self.right_frame)
        self.tree_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.search_top_frame = tk.Frame(self.search_frame)
        self.search_top_frame.pack(side=tk.TOP, fill=tk.X)
        self.search_bottom_frame = tk.Frame(self.search_frame)
        self.search_bottom_frame.pack(side=tk.BOTTOM, fill=tk.X) 


        #create button
        self.info_button = tk.Button(self.left_frame, text="Info", command=self.info)
        self.add_button = tk.Button(self.left_frame, text="Tilføj bog", command=self.add_book)
        self.delete_button = tk.Button(self.left_frame, text="Slet bog", command=self.delete_book)
        self.update_button = tk.Button(self.left_frame, text="Opdater bog", command=self.update_book)

        self.info_button.pack()
        self.add_button.pack()
        self.delete_button.pack()
        self.update_button.pack()

        #create treeview
        columns = ("Titel", "Forfatter", "Genre", "Produktkode")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH,  expand=True)
        
        #create scrollbar
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.configure(yscrollcommand=vsb.set)

        #create search bar list
        self.search_bars = []
        #used instead of keypressed as it only gives update on change and not if no change occurs
        self.search_sv = []

        #create columns
        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=1)

            #add search entry above for each column
            sv = tk.StringVar()
            sv.trace_add("write", self.search)
            
            search_bar = tk.Entry(self.search_bottom_frame, textvariable=sv)
            search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

            #must be kept alive
            self.search_sv.append(sv)
            self.search_bars.append(search_bar)

        #allow only numbers for product code
        self.search_bars[3].configure(validate=tk.ALL, validatecommand=((self.register(self._entry_restrict_numbers)), '%P'))

        #add search title in top search frame
        search_title = tk.Label(self.search_top_frame, text="Søg efter bøger", font='Helvetica 15 bold')
        search_title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        #sort by option
        sort_by_options = []

        #variable for sort by option
        self.sort_by = tk.StringVar()
        self.sort_by.set(sort_by_options[0])   
        self.sort_by.trace_add("write", self.search)
        
        #menu
        self.w = tk.OptionMenu(self.search_top_frame, self.sort_by, *sort_by_options)
        self.w.pack(side=tk.RIGHT, fill=tk.X, expand=True)


        #populate treeview
        self.populate_tree()
        
    def _entry_restrict_numbers(self, P):
        if P.isdigit() or P == "":
            return True
        else:
            return False

    def populate_tree(self, search: Book_Search_Query=Book_Search_Query()):
        self.tree.delete(*self.tree.get_children())
        for book in self.db.get_minbooks(search):
            self.tree.insert("", tk.END, values=(book.title or self.none_item, book.author or self.none_item, book.genre or self.none_item, book.product_code or self.none_item))

    def info(self):
        pass

    def add_book(self):
        pass

    def delete_book(self):
        pass

    def update_book(self):
        pass
    
    def search(self, *args):
        search = Book_Search_Query(
            title=self.search_sv[0].get() or None, 
            author=self.search_sv[1].get() or None, 
            genre=self.search_sv[2].get() or None, 
            product_code=self.search_sv[3].get() or None)
        self.populate_tree(search)



if __name__ == "__main__":
    app = App()
    app.mainloop()