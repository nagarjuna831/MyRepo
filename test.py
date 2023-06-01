from tkinter import Tk, Label
from PIL import ImageTk, Image

root = Tk()

# Create a Label widget to hold the background image
background_label = Label(root)

# Load the image
image = Image.open("epsum.png")
background_image = ImageTk.PhotoImage(image)

# Set the image as the background of the Label
background_label.config(image=background_image)
background_label.pack(fill="both", expand=True)

root.mainloop()