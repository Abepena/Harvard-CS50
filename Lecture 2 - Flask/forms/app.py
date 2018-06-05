from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello', methods=["GET","POST"])
def hello():
    """
    someone submits form with their name 
    name gets the request form and gets whetever is called name is 'name'
    """
    if request.method == "GET":
        return "Please submit the form instead."
    else:
        name = request.form.get("name")
        return render_template('hello.html', name= name)

if __name__ == '__main__':
    app.run()