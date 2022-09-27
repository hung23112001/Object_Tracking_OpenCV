from tkinter import *
from tkinter import Tk
from tkinter import ttk
import tkinter
import Packages as pk


def active_win():
    try:
        _, _ = variable.get().split('x')
        root.destroy()
        new_root = Tk()
        win = pk.Window(new_root, variable.get())
        win()
        new_root.mainloop()
    except:
        tkinter.messagebox.showerror(title='Lỗi', message='Vui lòng chọn kích thước cửa sổ')


OPTIONS = ["        ", "1920x1080", "1280x720", "1024x768"]
root = Tk()
root.geometry('200x250')
variable = StringVar(root)
variable.set(OPTIONS[0])
text = ttk.Label(root, text='Chọn kích thước cửa sổ')
select = ttk.OptionMenu(root, variable, *OPTIONS)
button = ttk.Button(root, text='Run',
                    width=22, command=active_win)
text.pack()
select.pack()
button.pack()

root.iconbitmap('./Assets/icon.ico')
root.mainloop()
