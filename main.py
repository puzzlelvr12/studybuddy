from flask import Flask, request, render_template_string
import openai
import pytesseract
from PIL import Image
from io import BytesIO
import os

# OpenAI setup
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Optional: Tesseract Windows setup (uncomment and set path if not in PATH)
#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


app = Flask(__name__)

TEMPLATE = '''
<h2>🤖 StudyBuddy (Free): AI Answers from Text or Image!</h2>
<form method="post" enctype="multipart/form-data">
  <input name="user_input" style="width:60%%" placeholder="Type a question (e.g. 'How do I solve this?')" autofocus>
  <input type="file" name="image_file" accept="image/*" style="margin-left:10px;">
  <button>Go</button>
</form>
{% if extracted %}
  <div style="margin-top:15px;"><b>Extracted Image Text:</b>
  <pre style="background:#f0f0f0; padding:4px 7px;">{{ extracted }}</pre></div>
{% endif %}
{% if response %}
  <div style="margin-top:20px;">
    <b>AI Bot:</b>
    <div style="white-space:pre-wrap; background: #ecefff; padding: 6px 10px;">{{ response }}</div>
  </div>
{% endif %}
{% if error %}
  <p style="color: red;"><b>Error:</b> {{ error }}</p>
{% endif %}
'''

def ask_gpt(prompt):
    system_msg = (
        "You are a friendly and helpful study tutor. If user uploads text from notes, images, math problems, or science content, explain, solve, and walk them through the process step by step."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def extract_text_from_image(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return ""

@app.route('/', methods=['GET', 'POST'])
def home():
    answer = None
    error = None
    extracted = None
    user_input = None
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        image_file = request.files.get('image_file')
        ocr_text = ""
        if image_file and image_file.filename != '':
            ocr_bytes = image_file.read()
            ocr_text = extract_text_from_image(ocr_bytes)
            extracted = ocr_text
        # Build prompt: If there is OCR and user input, join BOTH ("How do I solve this?\n\n[extracted text]")
        if ocr_text and user_input:
            full_prompt = f"{user_input}\n\nHere is the content from my image:\n{ocr_text}"
        elif ocr_text:
            full_prompt = f"Please explain, solve, or analyze this image text:\n{ocr_text}"
        elif user_input:
            full_prompt = user_input
        else:
            error = "Please enter a question or upload an image."
            full_prompt = None

        if full_prompt and not error:
            try:
                answer = ask_gpt(full_prompt)
            except Exception as e:
                error = f"AI error: {e}"

    return render_template_string(TEMPLATE, response=answer, error=error, extracted=extracted)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
