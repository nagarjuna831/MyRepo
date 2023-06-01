# from tkinter import filedialog
# from tkinter import *
# root = Tk()
# root.withdraw()
# folder_selected = filedialog.askdirectory()
#-----------------------------------------------------
#Import the Tkinter library
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
#Create an instance of Tkinter frame
win= Tk()
#Define the geometry
win.geometry("750x250")
def select_folder():
   path= filedialog.askopenfilename(title="Select a File", filetype=(('pdf files','*.pdf'),('all files','*.*')))
   Label(win, text=path, font=13).pack()
#Create a label and a Button to Open the dialog
Label(win, text="Click the Button to Select a folder to merge files", font=('Aerial 18 bold')).pack(pady=20)
button= ttk.Button(win, text="Select", command= select_folder)
button.pack(ipadx=5, pady=15)
win.mainloop()