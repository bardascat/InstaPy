"""
Main module of the server file
"""

import connexion


# Create the application instance
app = connexion.App(__name__, specification_dir='./')

# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml')


# create a URL route in our application for "/"
@app.route('/')
def home():
    return "ANGIE PYTHON REST API"


if __name__ == '__main__':
    app.run(debug=False)
