from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm Samuel Fobi-Berko! and I've got news for you 'it ain't easy'"

if __name__ == '__main__':
    app.run(debug=True)
