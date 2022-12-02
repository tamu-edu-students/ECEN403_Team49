import tkinter as tk
from tkinter import *
from tkinter import ttk

# Create parent window
root = tk.Tk()
root.title("Solar Panel Charging System")

tabControl = ttk.Notebook(root)

tabDat = ttk.Frame(tabControl)
tabAni = ttk.Frame(tabControl)
tabCtl = ttk.Frame(tabControl)

tabControl.add(tabDat, text='Data and Graphs')
tabControl.add(tabAni, text='System Animation')
tabControl.add(tabCtl, text='Control Systems')

tabControl.pack(expand=1, fill="both")

ttk.Label(tabDat, text='Welcome to GeeksForGeeks').grid(column=0, row=1, padx=50, pady=50)
ttk.Label(tabAni, text='Lets dive into the world of computers').grid(column=0, row=0, padx=30, pady=30)

root.mainloop()