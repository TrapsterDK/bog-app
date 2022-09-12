import tkinter as tk
from tkinter import ttk
from database import *

#class for tkinter app
class App(tk.Tk):
    def __init__(self, db_name="database.db"):
        super().__init__()
        self.db = Database(db_name)
        self.title("Bog butik")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        #split screen into two frames (left and right) one with buttons one with treeview expand on y axis
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx= 10, pady=10)

        #create buttons
        self.add_button = tk.Button(self.left_frame, text="Tilføj bog", command=self.add_book)
        self.add_button.pack()
        self.delete_button = tk.Button(self.left_frame, text="Slet bog", command=self.delete_book)
        self.delete_button.pack()
        self.update_button = tk.Button(self.left_frame, text="Opdater bog", command=self.update_book)
        self.update_button.pack()

        #create treeview
        self.tree = ttk.Treeview(self.right_frame, columns=("title", "author", "genre", "product_code"), show='headings')
        self.tree.heading("title", text="Titel")
        self.tree.heading("author", text="Forfatter")
        self.tree.heading("genre", text="Genre")
        self.tree.heading("product_code", text="Produktkode")
        self.tree.pack(fill=tk.Y, expand=True)

        
        #populate treeview
        self.populate_tree()

    def populate_tree(self, search: Book_Search_Query=Book_Search_Query()):
        self.tree.delete(*self.tree.get_children())
        for book in self.db.get_minbooks(search):
            self.tree.insert("", tk.END, values=(book.title, book.author, book.genre, book.product_code))

    def add_book(self):
        pass

    def delete_book(self):
        pass

    def update_book(self):
        pass



if __name__ == "__main__":
    app = App()
    app.mainloop()