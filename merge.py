
import PyPDF2
import os 
from tkinter import Tk
from tkinter import filedialog

def select_folder():
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    if folder_path:
        print("Selected folder:", folder_path)
    return folder_path


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
        output_file = baseDir + '/' + patientName + '.pdf'
        merger.write(output_file)
        merger.close()

        print(f"PDF files merged successfully! -- {str(files).ljust(80)} Merged into -- {output_file}")

baseDir = select_folder()
files = os . listdir (baseDir) 
pdfFiles = [ fileName  for fileName in files if fileName . endswith ('.pdf')]
#print ( pdfFiles )

patientNames = [ fileName.replace('_1.pdf', '') for fileName in pdfFiles if '_1' in fileName ]
patientNames =list(set( [ fileName [ : fileName . rindex ( '_' )  ] for fileName in pdfFiles if '_' in fileName  ]))

for patientName in patientNames:
   
    patientFiles = list( filter ( lambda fileName : fileName . startswith ( patientName ), pdfFiles ))
    
    patientFiles . sort (key = lambda fileName : int ( fileName . replace (f'{patientName}_', '').replace('.pdf', '')) if '_' in fileName else 0 )  
    
    merge_pdf_files(patientName, patientFiles)
    [ os . remove ( baseDir + '/' + file ) for file in  patientFiles if '_' in file ]
    
