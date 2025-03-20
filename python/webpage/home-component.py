from flask import Flask, render_template, jsonify, request
from shared.controls import get_counter, set_counter, increase_counter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/controls')
def controls():
    counter = get_counter()
    return render_template('controls.html', counter=counter)

@app.route('/increase', methods=['POST'])
def increase():
    increase_counter()
    return jsonify({'counter': get_counter()})

@app.route('/set_counter', methods=['POST'])
def set_new_counter():
    new_counter = request.json.get('counter', None)
    if new_counter is not None:
        set_counter(new_counter)
    return jsonify({'counter': get_counter()})

if __name__ == '__main__':
    app.run(debug=True)
