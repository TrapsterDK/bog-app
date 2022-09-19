from audioop import add
import tkinter as tk
from tkinter import Toplevel
from tkinter import *
from tkinter import ttk
import random
import math
import time
from turtle import left
import decimal
from database import *
from tkinter import messagebox


fontt = ("Segoe UI Black",12)




class Eksempel1(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self)
        root.update_idletasks()
        self.build_gui()
        self.db = Database()
       
    def error_message(self, str):
        messagebox.showerror("Fejl", str)

    def add_book(self):
        titel = self.add_titel_entry.get()
        forfatter = self.add_forfatter_entry.get().split(",")
        forfatter = [i.strip() for i in forfatter]
        genre = self.add_genre_entry.get().split(",")
        genre = [i.strip() for i in genre]
        x = decimal.Decimal(self.add_pris_entry.get())
        try:
            pris = decimal.Decimal(x)
        
        except decimal.ConversionSyntax:
            self.error_message("forkert input. Indtast et tal")
            
        
        lager = int(self.add_lager_entry.get())

        newbook = Book(title= titel,price = pris, stock = lager, authors = forfatter, genres = genre)
        self.db.add_books([newbook])
        

    def click(self,event, name, but):
        name.configure(state=NORMAL)
        name.delete(0, END)
        name.unbind('<Button-1>', but)
        print("click")

    def add_button_menu(self):
        add_menu = Toplevel(root)
        add_menu.geometry("200x140")
        add_menu.resizable(False, False)
        add_menu_vframe = Frame(add_menu)
        add_menu_hframe = Frame(add_menu)

        #entrys
        self.add_titel_entry = tk.Entry(add_menu_hframe)
        self.add_forfatter_entry = tk.Entry(add_menu_hframe)
        self.add_genre_entry = tk.Entry(add_menu_hframe)
        self.add_pris_entry = tk.Entry(add_menu_hframe)
        self.add_lager_entry = tk.Entry(add_menu_hframe)  
        annuler = tk.Button(add_menu_hframe, text = "afslut", command = add_menu.withdraw)
        gem = tk.Button(add_menu_hframe, text = "gem", command = self.add_book)

        self.add_titel_entry.pack(side = TOP, pady = 1)
        self.add_forfatter_entry.pack(side = TOP, pady = 1)
        self.add_genre_entry.pack(side = TOP, pady = 1)
        self.add_pris_entry.pack(side = TOP, pady = 1)
        self.add_lager_entry.pack(side = TOP, pady = 1) 
        gem.pack(side = RIGHT, pady = 4, anchor = NE)
        annuler.pack(side = RIGHT, padx = 10, pady = 4, anchor = NE)

        #text
        self.titel_label = tk.Label(add_menu_vframe, text = "titel: ")  
        self.forfatter_label = tk.Label(add_menu_vframe, text = "forfatter: ") 
        self.genre_label = tk.Label(add_menu_vframe, text = "genre: ") 
        self.pris_label = tk.Label(add_menu_vframe, text = "pris: ")
        self.lager_label = tk.Label(add_menu_vframe, text = "lager: ")  

        self.titel_label.pack(side = TOP, anchor=NW)
        self.forfatter_label.pack(side = TOP, anchor=NW)
        self.genre_label.pack(side = TOP, anchor=NW)
        self.pris_label.pack(side = TOP, anchor=NW)
        self.lager_label.pack(side = TOP, anchor=NW)

       
        #add_menu.mainloop()
        add_menu_vframe.pack(side=LEFT, fill = BOTH, expand = FALSE)
        add_menu_hframe.pack(side=LEFT, fill = BOTH, expand = FALSE)

    def build_gui(self):

        #Main Venstre og højre frame
        self.pack(fill = BOTH, expand = True)
        self.frame1 = tk.Frame(self,bg="#00655B", highlightbackground='red', highlightthickness = 0)
        self.frame2 = tk.Frame(self)
        self.frame1.pack(side = LEFT, fill=Y, expand = 0, ipadx = 30)
        self.frame2.pack(side = RIGHT, fill = BOTH, expand = True)

        #Højre frame 3-deling: Tekstfelt, button, tabel
        self.teksfelt_frame = tk.Frame(self.frame2)
        self.get_button_frame = tk.Frame(self.frame2)
        self.tabel_frame = tk.Frame(self.frame2)
        
        self.teksfelt_frame.pack()
        self.get_button_frame.pack()
        self.tabel_frame.pack()


        self.titel_entry = tk.Entry(self.teksfelt_frame)
        self.author_entry = tk.Entry(self.teksfelt_frame)
        self.genre_entry = tk.Entry(self.teksfelt_frame)
        self.id_entry = tk.Entry(self.teksfelt_frame)

        self.titel_entry.insert(0, "This is the default text")
        self.author_entry.insert(0, "This is the default text")
        self.genre_entry.insert(0, "This is the default text")
        self.id_entry.insert(0, "This is the default text")

        self.titel_entry.pack(side = LEFT)
        self.author_entry.pack(side = LEFT)
        self.genre_entry.pack(side = LEFT)
        self.id_entry.pack(side = LEFT)

        self.clicked1 = None
        self.clicked2 = None
        self.clicked3 = None
        self.clicked4 = None

        self.clicked1 = self.titel_entry.bind('<Button-1>', lambda Event : self.click(Event, self.titel_entry, self.clicked1))
        self.clicked2 = self.author_entry.bind('<Button-1>', lambda Event : self.click(Event, self.author_entry, self.clicked2))
        self.clicked3 = self.genre_entry.bind('<Button-1>', lambda Event : self.click(Event, self.genre_entry, self.clicked3))
        self.clicked4 = self.id_entry.bind('<Button-1>', lambda Event : self.click(Event, self.id_entry, self.clicked4))

        # Tabel

        my_game = ttk.Treeview(self.tabel_frame)

        my_game['columns'] = ('id', 'Titel', 'Forfatter', 'Genre', 'Pris', 'Lager')

        my_game.column("#0", width=0,  stretch=NO)
        my_game.column("id",anchor=CENTER, width=80)
        my_game.column("Titel",anchor=CENTER,width=80)
        my_game.column("Forfatter",anchor=CENTER,width=80)
        my_game.column("Genre",anchor=CENTER,width=80)
        my_game.column("Pris",anchor=CENTER,width=80)
        my_game.column("Lager",anchor=CENTER,width=80)


        my_game.heading("#0",text="",anchor=CENTER)
        my_game.heading("id",text="Id",anchor=CENTER)
        my_game.heading("Titel",text="Titel",anchor=CENTER)
        my_game.heading("Forfatter",text="Forfatter",anchor=CENTER)
        my_game.heading("Genre",text="Genre",anchor=CENTER)
        my_game.heading("Pris",text="Pris",anchor=CENTER)
        my_game.heading("Lager",text="Lager",anchor=CENTER)


        my_game.insert(parent='',index='end',iid=0,text='',
        values=('1','Ninja','101','Oklahoma', 'Moore', '12'))

        my_game.insert(parent='',index='end',iid=1,text='',
        values=('2','Ranger','102','Wisconsin', 'Green Bay', '42'))

        my_game.insert(parent='',index='end',iid=2,text='',
        values=('3','Deamon','103', 'California', 'Placentia', '521'))

        my_game.insert(parent='',index='end',iid=3,text='',
        values=('4','Dragon','104','New York' , 'White Plains', '421'))
        
        
        

        my_game.pack()


        #Buttons Left frame

        self.sell_button = tk.Button(self.frame1, text = "Sælg",)
        self.info_button = tk.Button(self.frame1, text = "info",)
        self.new_button = tk.Button(self.frame1, text = "tilføj bog", command = self.add_button_menu)

        self.sell_button.pack()
        self.info_button.pack()
        self.new_button.pack()

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)



root = tk.Tk()
prg = Eksempel1(root)
prg.master.title('Første brugerflade')
prg.mainloop()
