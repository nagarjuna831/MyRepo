#automatically merging code

import PyPDF2
import os 
from tkinter import *
from tkinter import filedialog
from tkinter import ttk 
from PIL import ImageTk, Image

def select_source_folder():
    global baseDir 
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    if folder_path:
        print("Selected folder:", folder_path)
    baseDir =  folder_path
def select_dest_folder():
    global outputDir
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    if folder_path:
        print("Selected folder:", folder_path)
    outputDir = folder_path


def merge_pdf_files( patientName, files ):
    #input_folder = filedialog.askdirectory(title="Select Input Folder")
    # Check if any files were selected
    #print ( files )
    if files:
        # Create a PDF merger object
        merger = PyPDF2.PdfMerger()

        # Merge selected PDF files
        for file in files:
            merger.append(baseDir + '/' + file)

        # Save the merged PDF file
        output_file = outputDir + '/' + patientName + '.pdf'
        merger.write(output_file)
        merger.close()

        print(f"PDF files merged successfully! -- {str(files).ljust(80)} Merged into -- {output_file}")

window = Tk () 
f0 = Frame ( window )
background_label = Label(f0, width=300)

# Load the image
image = Image.open("epsum.png")
background_image = ImageTk.PhotoImage(image)

# Set the image as the background of the Label
background_label.config(image=background_image)
background_label.pack(fill="both", expand=True )
f0.pack ( side = LEFT ) 


window.title('Epsumlabs Merger')
window.resizable(False, False)
window.geometry('600x300')

Label ( window , height=4) . pack ( )

f1 = Frame ( window, height=200) 
l1=Label ( f1, text = 'Enter source folder : ') 
#l1.pack ( side = LEFT)
b1 = Button (f1, text = 'Select SOURCE Folder', command = select_source_folder , width=30)
b1.pack( side = RIGHT )
f1.pack () 

Label ( window , height=1) . pack ( )

f2 = Frame () 
l2=Label ( f2, text = 'Enter destination folder : ') 
#l2.pack ( side = LEFT)
b2 = Button (f2, text = 'Select DESTINATION Folder', command = select_dest_folder , width=30)
b2.pack( side = RIGHT )
f2.pack () 
Label ( window , height=1) . pack ( )

def main () : 
    files = os . listdir (baseDir) 
    pdfFiles = [ fileName  for fileName in files if fileName . endswith ('.pdf')]
    #print ( pdfFiles )

    patientNames = [ fileName.replace('_1.pdf', '') for fileName in pdfFiles if '_1' in fileName ]
    patientNames =list(set( [ fileName [ : fileName . rindex ( '_' )  ] for fileName in pdfFiles if '_' in fileName  ]))

    for patientName in patientNames:
    
        patientFiles = list( filter ( lambda fileName : fileName . startswith ( patientName ), pdfFiles ))
        
        patientFiles . sort (key = lambda fileName : int ( fileName . replace (f'{patientName}_', '') . replace('.pdf', '')) if '_' in fileName else 0 )  
        
        merge_pdf_files(patientName, patientFiles)
        [ os . remove ( baseDir + '/' + file ) for file in  patientFiles if '_' in file ]

f3 = Frame () 
def exitp () : 
    exit ( 0 )
Button ( f3, text = 'Merge' , command = main, height=2, width=19, bg='green' ).pack ( side = LEFT ) 
Button ( f3, text = 'Exit' , command = exitp, height=2, width=10, bg='red' ).pack ( side = RIGHT ) 
f3.pack () 
window . mainloop () 