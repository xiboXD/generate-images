from flask import Flask, render_template
import os

app = Flask(__name__, template_folder='output_html')

@app.route('/')
def index():
    output_html_folder = 'output_html'
    html_files = [f for f in os.listdir(output_html_folder) if f.endswith('.html')]
    html_files = sorted(html_files)
    return render_template('index.html', html_files=html_files)

@app.route('/<filename>')
def show_html(filename):
    return render_template(filename)

if __name__ == '__main__':
    app.run(port=8000)
