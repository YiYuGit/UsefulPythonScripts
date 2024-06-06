# This is the newer version of Splitting Boring Log append
# Bulild this into executable using "pyinstaller --onefile scriptName.py" command.
# the app will ask user to set a x1,y1,x2,y2 area of the pdf file page ( the origin of x and y are the upper left corner of pdf page, measured in points, 1 in = 72points)
# the starting page can help user skip the starting blank page.( type the natural page number, staring with 1), script will handle it and translate to the index starting with 0
# in the first step, the app will determine if the text area can be read out or not and choose the correct to get the text
# text extraced or ocr-ed from pdf page will be stored in the csv file for user to review, 
# after reviewing and correcting wrong numbers, user can click 2nd step the split the big pdf into smaller files the contains same text ( the boring number).




import os
import csv
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
from tkinter import Tk, filedialog, Label, Button, Entry

def extract_text_from_location(pdf_path, page_number, x1, y1, x2, y2):
    try:
        pdf_document = fitz.open(pdf_path)
        page = pdf_document.load_page(page_number)
        rect = fitz.Rect(x1, y1, x2, y2)
        text = page.get_text('text', clip=rect)
        pdf_document.close()
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def ocr_part_of_pdf(pdf_path, page_number, x1, y1, x2, y2):
    try:
        pdf_document = fitz.open(pdf_path)
        page = pdf_document.load_page(page_number)
        area = (x1, y1, x2, y2)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=area)
        pdf_document.close()
        
        ocr_pdf_document = fitz.open("pdf", pixmap.pdfocr_tobytes(compress=True, language='eng', tessdata=tessdata_path))
        ocr_page = ocr_pdf_document.load_page(0)
        text = ocr_page.get_text()
        ocr_pdf_document.close()
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""

def determine_type(pdf_path, page_number, x1, y1, x2, y2):
    test_text = extract_text_from_location(pdf_path, page_number, x1, y1, x2, y2)
    if test_text != "":
        return False
    else: 
        return True

def generate_csv(pdf_path, start_page, x1, y1, x2, y2, ocr_or_not):
    csv_path = os.path.splitext(pdf_path)[0] + '.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Page Number', 'Extracted Text'])
        
        with open(pdf_path, 'rb') as input_file:
            pdf_reader = PdfReader(input_file)
            total_pages = len(pdf_reader.pages)        
            
            if ocr_or_not:
                for i in range(start_page - 1, total_pages):
                    ocr_text = ocr_part_of_pdf(pdf_path, i, x1, y1, x2, y2)
                    ocr_clean_text = clean_special_text(ocr_text)
                    csv_writer.writerow([i + 1, ocr_clean_text])  # Adjust for human-readable page numbering
            else:
                for i in range(start_page - 1, total_pages):
                    read_text = extract_text_from_location(pdf_path, i, x1, y1, x2, y2)
                    read_clean_text = clean_special_text(read_text)
                    csv_writer.writerow([i + 1, read_clean_text])  # Adjust for human-readable page numbering
    
    button2.config(state="normal")  # Enable the split file button once CSV is written
    return csv_path                

def split_pdf_from_csv(pdf_path, csv_path, output_folder):
    try:
        pdf_reader = PdfReader(pdf_path)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            current_special_text = ''
            current_section_pages = []

            for row in csv_reader:
                page_number, text = row
                page_number = int(page_number) - 1  # Convert back to zero-indexed page number
                clean_text = clean_special_text(text)

                if clean_text != current_special_text:
                    if current_section_pages:
                        output_pdf_path = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(pdf_path))[0]}_{current_special_text}.pdf')
                        with open(output_pdf_path, 'wb') as output_file:
                            pdf_writer = PdfWriter()
                            for page in current_section_pages:
                                pdf_writer.add_page(page)
                            pdf_writer.write(output_file)

                    current_special_text = clean_text
                    current_section_pages = [pdf_reader.pages[page_number]]
                else:
                    current_section_pages.append(pdf_reader.pages[page_number])

            if current_section_pages:
                output_pdf_path = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(pdf_path))[0]}_{current_special_text}.pdf')
                with open(output_pdf_path, 'wb') as output_file:
                    pdf_writer = PdfWriter()
                    for page in current_section_pages:
                        pdf_writer.add_page(page)
                    pdf_writer.write(output_file)
    except Exception as e:
        print(f"Error splitting PDF: {e}")

def clean_special_text(text):
    invalid_chars = '\\/:*?"<>|,'
    for char in invalid_chars:
        text = text.replace(char, '_')
    text = text.strip()
    return text

def generate_csv_and_run(pdf_path, start_page, x1, y1, x2, y2):
    button2.config(state="disabled")  # Disable the split file button
    ocr_or_not = determine_type(pdf_path, start_page - 1, x1, y1, x2, y2)
    generate_csv(pdf_path, start_page, x1, y1, x2, y2, ocr_or_not)

def select_pdf_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path

def select_csv_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    return file_path

def run_1st_step():
    pdf_path = select_pdf_file()
    if pdf_path:
        start_page = int(entry_start_page.get())
        x1 = int(entry_x1.get())
        y1 = int(entry_y1.get())
        x2 = int(entry_x2.get())
        y2 = int(entry_y2.get())
        generate_csv_and_run(pdf_path, start_page, x1, y1, x2, y2)

def run_2nd_step():
    csv_path = select_csv_file()
    output_folder = os.path.splitext(csv_path)[0] + '_output'
    split_pdf_from_csv(os.path.splitext(csv_path)[0] + '.pdf', csv_path, output_folder)

def load_settings():
    settings_file = 'settings.txt'
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            line = file.readline().strip()
            try:
                x1, y1, x2, y2 = map(int, line.split(','))
            except ValueError:
                x1, y1, x2, y2 = 360, 70, 432, 90
    else:
        x1, y1, x2, y2 = 360, 70, 432, 90
    return x1, y1, x2, y2

# Load settings
x1_default, y1_default, x2_default, y2_default = load_settings()

# The ocr data sys.executable
folder_path = os.path.dirname(os.path.abspath(sys.executable))
# For using script directly, use this line
#folder_path = os.path.dirname(os.path.abspath(__file__))

tessdata_path = os.path.join(folder_path, "tessdata")

# Create GUI main window
root = Tk()
root.title("Boring Log Splitting Tool")

label1 = Label(root, text="Step 1: Select PDF file and Set Coordinates")
label1.pack()

label_start_page = Label(root, text="Starting Page Number:")
label_start_page.pack()
entry_start_page = Entry(root)
entry_start_page.pack()
entry_start_page.insert(0, "1")

label_x1 = Label(root, text="x1:")
label_x1.pack()
entry_x1 = Entry(root)
entry_x1.pack()
entry_x1.insert(0, str(x1_default))

label_y1 = Label(root, text="y1:")
label_y1.pack()
entry_y1 = Entry(root)
entry_y1.pack()
entry_y1.insert(0, str(y1_default))

label_x2 = Label(root, text="x2:")
label_x2.pack()
entry_x2 = Entry(root)
entry_x2.pack()
entry_x2.insert(0, str(x2_default))

label_y2 = Label(root, text="y2:")
label_y2.pack()
entry_y2 = Entry(root)
entry_y2.pack()
entry_y2.insert(0, str(y2_default))

button1 = Button(root, text="Select PDF and Generate CSV", command=run_1st_step)
button1.pack()

label2 = Label(root, text="Step 2: Inspect and Correct CSV File, then click Split File")
label2.pack()

button2 = Button(root, text="Split File", command=run_2nd_step, state="disabled")
button2.pack()

root.mainloop()
