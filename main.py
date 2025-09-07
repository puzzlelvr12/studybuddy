from flask import Flask, request, render_template_string
import openai
import os

# Get your OpenAI API key from environment variable
api_key = os.environ['OPENAI_API_KEY']
client = openai.OpenAI(api_key=api_key)

app = Flask(__name__)

TEMPLATE = '''
<h2>🤖 AI Study Chatbot</h2>
<form method="post">
  <input name="user_input" style="width:60%%" autofocus required>
  <button>Ask</button>
</form>
{% if response %}
  <p><b>Bot:</b> {{ response }}</p>
{% endif %}
'''

def ask_gpt(prompt):
    system_msg = (
        "You are a helpful study assistant. Answer questions clearly and always "
        "follow up with a critical thinking question to help the student deepen their understanding."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

@app.route('/', methods=['GET', 'POST'])
def home():
    answer = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        answer = ask_gpt(user_input)
    return render_template_string(TEMPLATE, response=answer)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
