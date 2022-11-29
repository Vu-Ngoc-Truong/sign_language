from PIL import Image
import pytesseract

# img = Image.open("data/A/123.jpg")
# img.show("Example")

# path_to_tesseract = r"/home/ngoctruong/.local/bin/pytesseract"
# pytesseract.pytesseract.tesseract_cmd(path_to_tesseract)

# If you don't have tesseract executable in your PATH, include the following:
# pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

# Simple image to string
print(pytesseract.image_to_string(Image.open('text_2_vi.png'), lang='vi'))

# In order to bypass the image conversions of pytesseract, just use relative or absolute image path
# NOTE: In this case you should provide tesseract supported images or tesseract will return error
# print(pytesseract.image_to_string('test.png'))

# List of available languages
print(pytesseract.get_languages(config=''))

# French text image to string
# print(pytesseract.image_to_string(Image.open('test-european.jpg'), lang='fra'))
