import tkinter as tk
from PIL import Image, ImageGrab
import pytesseract
import subprocess
import re
import os

# Set Tesseract data path.  Make sure this path is correct!
os.environ['TESSDATA_PREFIX'] = r'C:\Tesseract-OCR\tessdata'

pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe' # Or your actual path
x1, y1, x2, y2 = 0, 0, 0, 0


def take_screenshot():
    global x1, y1, x2, y2
    x1, y1, x2, y2 = 0, 0, 0, 0

    root.withdraw()

    def create_canvas_window(width, height):
      # ... (This inner function remains the same)

    def on_click(event):
      # ... (This inner function remains the same)


    def on_drag(event):
      # ... (This inner function remains the same)


    def on_release(event):
      # ... (This inner function remains the same)



    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    top, canvas = create_canvas_window(screen_width, screen_height)
    canvas.bind("<ButtonPress-1>", on_click)



    top.grab_set()
    root.wait_window(top)



def process_image(im):
    try:
        temp_image_path = "temp_screenshot.png"
        im = im.resize((im.width * 3, im.height * 3), Image.Resampling.LANCZOS) # Upscale for better OCR
        im.save(temp_image_path, dpi=(300, 300))

        print(f"Screenshot saved to: {temp_image_path}")  # Logging


        command = [
            pytesseract.pytesseract.tesseract_cmd,
            temp_image_path,
            "stdout",
            "--psm", "auto_osd",
            "--tessdata-dir", r"C:\Tesseract-OCR\tessdata", # Make sure this path is accurate.
            "-l", "jpn",  # Explicitly setting to Japanese for now. Change to -l osd for auto-detection.
            "tsv"
        ]

        process = subprocess.run(command, capture_output=True, text=True, check=True)
        ocr_output = process.stdout

        print(f"Raw OCR output:\n{ocr_output}")  # Logging

        non_english_words = []
        for line in ocr_output.strip().split('\n')[1:]:  # Skip the header line
            parts = line.split('\t')

            if len(parts) >= 12:  # Error handling
                word = parts[11]
                print(f"Processing word: {word}") # Logging

                # Regular expression to filter out English words and whitespace
                if word.strip() != "" and not re.fullmatch(r'[a-zA-Z0-9\s]+', word):  
                    try:
                        x, y, w, h = int(parts[6]), int(parts[7]), int(parts[8]), int(parts[9])
                        non_english_words.append({'word': word, 'x': x, 'y': y, 'width': w, 'height': h})
                    except (ValueError, IndexError) as e: # Error handling
                        print(f"Error parsing line: {line}. Skipping. Error: {e}")



        os.remove(temp_image_path)

        if non_english_words:
            print("Extracted Non-English words/sentences:")
            for item in non_english_words:
                print(item)
        else:
            print("No non-English words found in the screenshot.")

    except subprocess.CalledProcessError as e:
        print(f"Error during OCR: {e.stderr}")  # Print stderr for debugging
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



root = tk.Tk()
root.geometry("200x100")
root.title("Screenshot Translator")

screenshot_button = tk.Button(root, text="Take Screenshot", command=take_screenshot)
screenshot_button.pack(pady=20)



root.mainloop()