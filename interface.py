import tkinter as tk
from tkinter import Toplevel
from tkinter import *
from tkinter import ttk
from tkinter.colorchooser import askcolor
import random
import math
import time

fontt = ("Segoe UI Black",12)
click_num = 0
click_numm = 0
xx1 = 0
xx2 = 0
yy1 = 0
yy2 = 0
buttonpressed = None



class Eksempel1(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self)
        #sroot.geometry("800x500")
        root.update_idletasks()
        self.build_gui()
        self.active_tool = ""
        self.current_color = "#000000"
        self.can_color.configure(bg=self.current_color)
        self.current_width = None

    def tegn_firkant(self):
        self.active_tool = "Firkant"

    def tegn_cirkel(self):
        self.active_tool = "Cirkel"

    def tegn_linje(self):
        self.active_tool = "Linje"

    def tegn_klinje(self):
        global click_numm
        self.active_tool = "Kontinuert linje"
        click_numm = 0

    def tegn_gardin(self):
        self.active_tool = "Gardin"

    def tegn_sgardin(self):
        self.active_tool = "smooth Gardin"

    def tegn_spray(self):
        self.active_tool = "Spray"

    def canvas_release(self,event):
        self.spray_active = False

    def Sprayy(self):
        circle_x = self.spray_pos[0]
        circle_y = self.spray_pos[1]
        for i in range (20):
            a = random.random() * 2 * math.pi
            r = 20 * math.sqrt(random.random())
            x = r * math.cos(a) + circle_x
            y = r * math.sin(a) + circle_y
            self.canvas.create_line(x,y,x+1,y+1, fill = self.current_color)
        if self.spray_active:
            self.after(80, self.Sprayy)

    def canvas_click(self, event):
        global buttonpressed
        buttonpressed = True
        global click_numm,xx1,xx2,yy1,yy2
        if self.active_tool == "Firkant":
            self.canvas.create_rectangle(event.x-10, event.y-10, event.x+10, event.y+10, fill=self.current_color, outline=self.current_color)
        elif self.active_tool == "Cirkel":
            self.canvas.create_oval(event.x-10, event.y-10, event.x+10, event.y+10, fill=self.current_color, outline=self.current_color)
        elif self.active_tool == "Linje":
            global click_num
            global x1,y1
            if click_num == 0:
                x1=event.x
                y1=event.y
                click_num = 1
            else:
                x2=event.x
                y2=event.y
                click_num = 0
                self.canvas.create_line(x1,y1,x2,y2, fill=self.current_color, width=5)

        elif self.active_tool == "Gardin":
            rgb = self.get_rgb()


            for i in range(10):
                r,g,b = rgb
                r *= i/10
                g *= i/10
                b *= i/10
                self.current_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
                self.canvas.create_rectangle(event.x-10, event.y-10, event.x+10, event.y+10, fill = self.current_color, outline = self.current_color)
                event.y += 20
                #print(self.current_color)

        elif self.active_tool == "smooth Gardin":
            rgb = self.get_rgb()
            r,g,b = rgb
            rstep = r / 255
            gstep = g / 255
            bstep = b / 255
            rr = 0
            gg = 0
            bb = 0
            for i in range(255):
                r,g,b = rgb
                rr += rstep
                gg += gstep
                bb += bstep
                self.current_color = f"#{int(rr):02x}{int(gg):02x}{int(bb):02x}"
                self.canvas.create_rectangle(event.x-10, event.y-0.5, event.x+10, event.y+0.5, fill = self.current_color, outline = self.current_color)
                event.y += 1



        elif self.active_tool == "Kontinuert linje":
            global click_numm,xx1,xx2,yy1,yy2

            if click_numm == 0:
                del click_numm
                del xx1
                del xx2
                del yy1
                del yy2
                xx1=event.x
                yy1=event.y
                click_numm = 1
            elif click_numm == 1:
                xx2=event.x
                yy2=event.y
                click_numm = 2
                self.canvas.create_line(xx1,yy1,xx2,yy2, fill=self.current_color, width=5)

            elif click_numm == 2:
                xx1 = xx2
                yy1 = yy2
                xx2 = event.x
                yy2 = event.y
                self.canvas.create_line(xx1,yy1,xx2,yy2, fill=self.current_color, width=5)

        elif self.active_tool == "Spray":
            self.spray_active = True
            self.spray_pos = (event.x, event.y)
            self.Sprayy()








    def get_rgb(self):
        r = int(self.sc_r.get())
        g = int(self.sc_g.get())
        b = int(self.sc_b.get())
        return (r,g,b)




    def change_color(self, event):
        r = int(self.sc_r.get())
        g = int(self.sc_g.get())
        b = int(self.sc_b.get())
        self.current_color = f"#{r:02x}{g:02x}{b:02x}"
        self.can_color.configure(bg=self.current_color)


    def clear_canvas(self):
        self.canvas.delete("all")


    def build_gui(self):


        self.pack(fill = BOTH, expand = True)
        self.frame1 = tk.Frame(self,bg="#00655B", highlightbackground='red', highlightthickness = 0)
        self.frame2 = tk.Frame(self)
        self.frame1.pack(side = LEFT, fill=Y, expand = 0, ipadx = 30)
        self.frame2.pack(side = RIGHT, fill = BOTH, expand = True)

        self.frame3 = tk.Frame(self.frame2, bg = "#00655B")
        self.frame4 = tk.Frame(self.frame2, bg = "yellow")
        self.frame3.pack(side = TOP, fill = X, expand = 0)
        self.frame4.pack(side = BOTTOM, fill = BOTH, expand= True)

        #Knapper
        but_color = "#A1B56F"
        ac_color = "#00655B"

        #venstre frame
        self.but_knap1 = tk.Button(self.frame1, font = fontt, text="Firkant",activebackground = ac_color ,bg = but_color, command = self.tegn_firkant)
        self.but_knap1.pack(fill = BOTH, expand = 1, pady = 5, padx = 4)
        CreateToolTip(self.but_knap1, text = "Vælg firkant")

        self.but_knap2 = tk.Button(self.frame1,font = fontt, text="Cirkel",activebackground = ac_color ,bg = but_color, command = self.tegn_cirkel)
        self.but_knap2.pack(fill = BOTH, expand = 1, pady = 5, padx = 4)

        self.linjeframe = tk.Frame(self.frame1,bg="#00655B")
        self.linjeframe.pack(fill = BOTH, expand = 1)
        self.but_knap3 = tk.Button(self.linjeframe,font = fontt, text="Linje",activebackground = ac_color ,bg = but_color, command = self.tegn_linje)
        self.but_knap5 = tk.Button(self.linjeframe,font = fontt, text="Kontinuert\nLinje",activebackground = ac_color ,bg = but_color, command = self.tegn_klinje)
        self.but_knap3.pack(side= LEFT,fill = BOTH, expand = 1, pady = 5, padx = 4)
        self.but_knap5.pack(side= LEFT,fill = BOTH, expand = 1, pady = 5, padx = 4)

        self.but_knap6 = tk.Button(self.frame1,font = fontt, text="Gardin",activebackground = ac_color ,bg = but_color, command = self.tegn_gardin)
        self.but_knap6.pack(fill = BOTH, expand = 1, pady = 5, padx = 4)

        self.but_knap8 = tk.Button(self.frame1,font = fontt, text="Smooth Gardin",activebackground = ac_color ,bg = but_color, command = self.tegn_sgardin)
        self.but_knap8.pack(fill = BOTH, expand = 1, pady = 5, padx = 4)

        self.but_knap9 = tk.Button(self.frame1,font = fontt, text="Spray Paint",activebackground = ac_color ,bg = but_color, command = self.tegn_spray)
        self.but_knap9.pack(fill = BOTH, expand = 1, pady = 5, padx = 4)


        self.but_knap4 = tk.Button(self.frame1,font = fontt, text="Clear Canvas",activebackground = ac_color ,bg = but_color, command = self.clear_canvas)
        self.but_knap4.pack(fill = BOTH, expand = 1, pady = 5, padx = 4)



        #højreop frame

        self.sc_r = tk.Scale(self.frame3,from_=0, to=255, orient=HORIZONTAL, bg = "red",command = self.change_color )
        self.sc_g = tk.Scale(self.frame3,from_=0, to=255, orient=HORIZONTAL, bg = "green",command = self.change_color)
        self.sc_b = tk.Scale(self.frame3,from_=0, to=255, orient=HORIZONTAL, bg = "blue", command = self.change_color)
        self.sc_r.pack(side = LEFT, padx = 5,pady = 2, ipadx = 10)
        self.sc_g.pack(side = LEFT, padx = 5,pady = 2, ipadx = 10)
        self.sc_b.pack(side = LEFT, padx = 5,pady = 2, ipadx = 10)
        '''
        self.sc_r.bind("<ButtonRelease>", self.change_color)
        self.sc_g.bind("<ButtonRelease>", self.change_color)
        self.sc_b.bind("<ButtonRelease>", self.change_color)
        '''
        #color window
        self.can_color = tk.Canvas(self.frame3, height = 35, width = 70)
        self.can_color.pack(side = LEFT, padx = 5,pady = 2, ipadx = 10)

        #Vælg farve
        self.color_button = tk.Button(self.frame3, text = "Vælg Farve", command= self.color_select)
        self.color_button.pack(side = LEFT, ipady = 5)

        #choose width
        '''
        self.sel_size = tk.LabelFrame(self.frame3, text="Size")
        self.sel_size.pack(side = LEFT)
        self.listbox = tk.Listbox(self.sel_size)
        self.listbox.insert(1,"1")
        self.listbox.insert(2, "2")
        self.listbox.insert(3, "3")
        self.listbox.insert(4, "4")
        self.listbox.pack()
        '''
        '''
        self.menubut = tk.Menubutton(self.frame3, text="Size", relief=RAISED)
        self.menubut.pack(side = LEFT, padx = 5,pady = 2, ipadx = 10 )
        self.menubut.menu = Menu( self.menubut, tearoff = 0 )
        self.menubut["menu"] = self.menubut.menu
        en = IntVar()
        to = IntVar()
        self.menubut.menu.add_checkbutton(label = "1",variable = en)
        self.menubut.menu.add_checkbutton(label = "1",variable = to)
        '''

        selected_width = tk.StringVar()
        self.sel_width = ttk.Combobox(self.frame3, textvariable=selected_width, width=3)
        self.sel_width['values'] = [[tal] for tal in range(50)]
        self.sel_width.pack(side = LEFT, padx=5, pady=5)


        #Main tegne Canvas
        self.canvas = tk.Canvas(self.frame4, bg = "white", cursor = "tcross")
        self.canvas.pack(fill = BOTH, expand = True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        #self.canvas.bind("<B1-Motion>",self.canvas_click)

    def color_select(self):
        self.sc_r.set(0)
        self.sc_g.set(0)
        self.sc_b.set(0)
        rgb, colors = askcolor(title="Tkinter Color Chooser")
        self.current_color = colors
        self.can_color.configure(bg=colors)








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
