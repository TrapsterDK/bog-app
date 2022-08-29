import tkinter as tk

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        #gui

def main():
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()