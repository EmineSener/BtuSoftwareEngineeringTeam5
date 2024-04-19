from flask import Flask, render_template
import json
app = Flask(__name__)
@app.route('/')
def index():
    with open('data.json') as f:
        data = json.load(f)
    return render_template('index.html', muzik=data['muzik'], makale1=data['makale1'],makale2=data['makale2'], film=data['film']
                           , dizi=data['dizi'], kitap=data['kitap'],wp=data['wp'], sadeceSen=data['sadeceSen'])

if __name__ == "__main__":
    app.run(debug=True)
