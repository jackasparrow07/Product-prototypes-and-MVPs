import tkinter as tk
from tkinter import Toplevel, messagebox
from PIL import ImageGrab, Image, ImageTk, ImageDraw, ImageFont
import pytesseract
from pytesseract import Output
from langdetect import detect
import google.generativeai as genai
from dotenv import load_dotenv
import os
import threading
import time
import re

# Load environment variables and configure API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("Gemini_api_key")
genai.configure(api_key=GOOGLE_API_KEY)


# Define Tesseract paths
pytesseract.pytesseract.tesseract_cmd = r"C:\Tesseract-OCR\tesseract.exe"  # Path to tesseract.exe
#pytesseract.pytesseract.tessdata_dir_config = r'--tessdata-dir "C:\Tesseract-OCR\tessdata"' # optional config 

class LLMProcessor:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def process(self, text):
        if not text:
            return None
        try:
            response = self.model.generate_content(text)
            return response.text
        except Exception as e:
            print(f"Error processing with Gemini: {e}")
            return None

class ScreenCaptureApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screenshot Translator")
        self.root.geometry("200x100")  # Small window
        self.llm_processor = LLMProcessor()  # Initialize Gemini LLM Processor
        
        # Add a button to take screenshot
        self.screenshot_button = tk.Button(self.root, text="Take Screenshot", command=self.start_screenshot_process)
        self.screenshot_button.pack(pady=20)
        
        self.image_path = "captured_area.png"
        
        # Create a label for notifications
        self.notification_label = tk.Label(self.root, text="", wraplength=200, justify="left")  # Add wraplength for better layout
        self.notification_label.pack(pady=10)
        
        # Create a label for extracted text
        self.extracted_text_label = tk.Label(self.root, text="", wraplength=200, justify="left")  # Add wraplength for better layout
        self.extracted_text_label.pack(pady=10)
        
        # Flag to stop the background thread
        self.stop_thread = False
        self.translation_thread = None


    def start_screenshot_process(self):
        # Minimize the main window and allow the user to select an area of the screen
        self.root.withdraw()
        self.screenshot_window = tk.Toplevel(self.root)
        self.screenshot_window.attributes('-fullscreen', True)
        self.screenshot_window.attributes('-alpha', 0.3)  # Transparent window
        self.screenshot_window.config(cursor="cross")  # Change cursor to cross
        self.canvas = tk.Canvas(self.screenshot_window, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.start_x = None
        self.start_y = None
        self.rect = None

        # Bind mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        # Record the starting point of the rectangle
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline='red', width=2)

    def on_mouse_drag(self, event):
        # Update the size of the rectangle as the user drags the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        # Capture the selected area and return focus to the main app window
        end_x, end_y = event.x, event.y
        self.capture_area(self.start_x, self.start_y, end_x, end_y)
        self.screenshot_window.destroy()  # Close the screenshot selection window
        self.root.deiconify()  # Restore the main app window
        self.preview_image()  # Show the preview window after capture

    def capture_area(self, x1, y1, x2, y2):
        # Convert canvas coordinates to screen coordinates
        x1 = self.screenshot_window.winfo_rootx() + x1
        y1 = self.screenshot_window.winfo_rooty() + y1
        x2 = self.screenshot_window.winfo_rootx() + x2
        y2 = self.screenshot_window.winfo_rooty() + y2

        # Capture the selected area of the screen and save it
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        screenshot.save(self.image_path)

    def preview_image(self):
        # Create a new window to preview the captured image
        preview_window = Toplevel(self.root)
        preview_window.title("Image Preview")
        preview_window.geometry("600x400")

        # Load and display the captured image
        captured_image = Image.open(self.image_path)
        img_resized = captured_image.resize((600, 400), Image.LANCZOS)  # Resize for preview
        img_tk = ImageTk.PhotoImage(img_resized)

        label = tk.Label(preview_window, image=img_tk)
        label.image = img_tk  # Keep a reference to avoid garbage collection
        label.pack()
        
        # Close the preview window after 3 seconds
        preview_window.after(3000, preview_window.destroy)


        # Start processing in the background
        self.stop_thread = False
        self.translation_thread = threading.Thread(target=self.process_image_async)
        self.translation_thread.start()


    def process_image_async(self):
        # Load the saved image and pass it through the OCR and translation pipeline
        captured_image = Image.open(self.image_path)
        
        # Perform OCR and translation
        words_with_positions = self.extract_text_with_positions(captured_image)
        words_with_languages = self.detect_languages(words_with_positions)
        
        # Separate English and non-English words with their locations
        english_words = []
        non_english_words = []
        for word_data in words_with_languages:
            if word_data['language'] == 'en':
                english_words.append(word_data)
            else:
                non_english_words.append(word_data)
        
        # Display extracted text in the UI
        self.display_extracted_text(english_words, non_english_words)

        # Translation logic remains the same
        if not non_english_words:
            self.show_notification("No non-English words found to translate.")
        else:
            # Create a single string with all words and positions
            all_text = ""
            for word_data in english_words:
                all_text += f"English: {word_data['word']} at ({word_data['x']}, {word_data['y']})\n"
            for word_data in non_english_words:
                all_text += f"Non-English: {word_data['word']} at ({word_data['x']}, {word_data['y']})\n"

            # Send the combined text to the LLM
            self.show_notification("Sending text to Gemini...")
            translated_text = self.translate_all_text(all_text)
            if translated_text is not None:
                self.show_notification(f"Gemini Translation: {translated_text}")
                # Now replace the text on the image based on translated_text

    def translate_all_text(self, all_text):
        prompt = f"""
        Translate the non-english texts into english and keep the english parts as it is and display all the translated outputs as a single string.
        Here's the text from the image:
        {all_text}
        """
        translated_text = self.llm_processor.process(prompt)
        return translated_text


    def extract_text_with_positions(self, image):
        # Extract text using OCR, returning words with their bounding boxes
        ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT)
        words = []
        for i in range(len(ocr_data['text'])):
            if ocr_data['text'][i].strip() != '':
                word_data = {
                    'word': ocr_data['text'][i],
                    'x': ocr_data['left'][i],
                    'y': ocr_data['top'][i],
                    'width': ocr_data['width'][i],
                    'height': ocr_data['height'][i]
                }
                words.append(word_data)
        return words

    def detect_languages(self, words):
        for word_data in words:
            try:
                word_data['language'] = detect(word_data['word'])
            except:
                word_data['language'] = 'unknown'
        return words

    def translate_words(self, words):
        for word_data in words:
            if word_data['language'] != 'en':  # Only translate non-English words
                translated_text = self.llm_processor.process(word_data['word'])
                word_data['translated_word'] = translated_text or word_data['word']  # Fallback to original word if no translation
                self.show_notification(f"Translated '{word_data['word']}' to '{translated_text or word_data['word']}'")
        return words

    def replace_text_on_image(self, image, words):
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        for word_data in words:
            if word_data['language'] != 'en':  # Only replace non-English words
                draw.rectangle(
                    [word_data['x'], word_data['y'], word_data['x'] + word_data['width'], word_data['y'] + word_data['height']],
                    fill='white'
                )
                translated_word = word_data.get('translated_word', word_data['word'])
                draw.text((word_data['x'], word_data['y']), translated_word, fill='black', font=font)
        
        return image

    def show_notification(self, message):
        self.notification_label.config(text=self.notification_label.cget("text") + message + "\n")  # Append new notifications
        
    def display_extracted_text(self, english_words, non_english_words):
        extracted_text = ""
        
        extracted_text += "English Words:\n"
        for word_data in english_words:
            extracted_text += f"Word: {word_data['word']}, Location: ({word_data['x']}, {word_data['y']})\n"
        
        extracted_text += "\nNon-English Words:\n"
        for word_data in non_english_words:
            extracted_text += f"Word: {word_data['word']}, Location: ({word_data['x']}, {word_data['y']})\n"
            
        self.extracted_text_label.config(text=extracted_text)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Bind closing event
        self.root.mainloop()

    def on_closing(self):
        # Stop the background thread when the main window is closed
        self.stop_thread = True
        if self.translation_thread is not None:
            self.translation_thread.join()
        self.root.destroy()

# Run the screen capture app
if __name__ == "__main__":
    app = ScreenCaptureApp()
    app.run()