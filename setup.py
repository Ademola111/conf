"""To start the webserver"""

from confapp import app

if __name__ == "__main__":
    app.run(debug=True, port=5000)