import pyautogui
import pytesseract
import re
import PIL.Image
import numpy as np
import os
import platform
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# --- User Flow and Workflow ---
# 1. User launches the application.
# 2. GUI window with "Screenshot" button appears.
# 3. User clicks the "Screenshot" button.
# 4. User clicks and drags to select a region of the screen.
# 5. The selected region is captured as a screenshot.
# 6. A timestamped directory is created within "screenshots" folder.
# 7. The screenshot is saved as "screenshot.png" in the directory.
# 8. OCR is performed on the saved screenshot.
# 9. Extracted text, positions, and dimensions are printed.
# 10. (Optional) Further processing on saved screenshot/data.


def get_tesseract_path():
    if platform.system() == "Windows":
        paths = [
            r"C:\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            rf"C:\Users\{os.getlogin()}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    elif platform.system() == "Darwin":  # macOS
        return "/usr/local/bin/tesseract"
    elif platform.system() == "Linux":  # Linux
        return "/usr/bin/tesseract"
    return None

def get_tessdata_path(tesseract_path):
    if not tesseract_path:
        return None
    tessdata_dir = os.path.join(os.path.dirname(tesseract_path), "tessdata")
    if os.path.exists(tessdata_dir):
        return tessdata_dir
    program_files = os.environ.get("ProgramFiles", "")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "")
    other_paths = [
        os.path.join(program_files, "Tesseract-OCR", "tessdata"),
        os.path.join(program_files_x86, "Tesseract-OCR", "tessdata")
    ]
    for path in other_paths:
        if os.path.exists(path):
            return path
    return None

def capture_and_analyze_area(region):
    tesseract_path = get_tesseract_path()
    if not tesseract_path:
        print("Error: Tesseract not found.")
        return

    tessdata_path = get_tessdata_path(tesseract_path)
    if not tessdata_path:
        print("Error: tessdata not found.")
        return

    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    config = f'--tessdata-dir "{tessdata_path}"'

    try:
        if region is None:
            print("No region selected.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join("screenshots", timestamp)
        os.makedirs(output_dir, exist_ok=True)

        screenshot = pyautogui.screenshot(region=region)
        screenshot_path = os.path.join(output_dir, "screenshot.png")
        screenshot.save(screenshot_path)

        screenshot_np = np.array(screenshot)
        gray = PIL.Image.fromarray(screenshot_np).convert('L')

        results = []
        data = pytesseract.image_to_data(gray, lang='eng+fra+deu+spa+ita+por+jpn+kor+chi_sim+chi_tra', config=config, output_type=pytesseract.Output.DICT)

        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 30 and data['text'][i].strip():
                word = data['text'][i]
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                results.append({'word': word, 'x': x, 'y': y, 'w': w, 'h': h})

        if not results:
            print("No text detected.")
            return

        print("Extracted words/characters and positions:")
        for item in results:
            print(f"{item['word']}: ({item['x']}, {item['y']}), w={item['w']}, h={item['h']}")

        # --- Optional further processing using 'results' and 'screenshot_path' ---

    except Exception as e:
        print(f"An error occurred: {e}")


def on_screenshot_button_click():
    print("Click and drag to select a region.")
    try:
        region = pyautogui.locateOnScreen('screenshot_button.png', confidence=0.9)  # Replace with your button image
        if region:
            x, y, width, height = region
            x -= 20
            y += height + 10
            width += 40
            height = 200  # Fixed height for screenshot region

            # --- Draw the red rectangle (visual cue) ---
            screenshot = pyautogui.screenshot(region=(x, y, width, height))  # Capture the initial area
            screenshot_np = np.array(screenshot)

            # Create a red rectangle overlay
            red_rectangle = np.zeros_like(screenshot_np)
            red_rectangle[:, :, 0] = 255  # Set red channel to 255

            # Overlay the red rectangle on the screenshot
            overlayed_image = PIL.Image.blend(PIL.Image.fromarray(screenshot_np), PIL.Image.fromarray(red_rectangle), alpha=0.5)

            # Display the overlayed image in a separate window
            overlayed_image.show()

            # --- End of red rectangle drawing ---

            capture_and_analyze_area((x, y, width, height))  # Capture and analyze after visual cue

            overlayed_image.close()  # Close the overlay window after capture

        else:
            print("Screenshot button not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def create_gui():
    root = tk.Tk()
    root.title("Screenshot & OCR")
    screenshot_button = ttk.Button(root, text="Screenshot", command=on_screenshot_button_click)
    screenshot_button.pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    create_gui()