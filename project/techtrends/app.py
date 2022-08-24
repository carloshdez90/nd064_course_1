from crypt import methods
import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
connections = 0


def get_db_connection():
    global connections
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connections += 1
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info(
            'The Article with id: "{}" does not exist!'.format(post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info(
            'The Article: "{}" was retrieved successfully!'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    app.logger.info("About Us page retrieved!")
    return render_template('about.html')

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            app.logger.info(
                'The Article: "{}" was created successfully!'.format(title))

            return redirect(url_for('index'))

    return render_template('create.html')


"""
### Custom endpoints to meet the project's requirements
"""


@app.route('/healtz')
def health_check():
    response = app.response_class(
        response=json.dumps({"result": "ok - healthy"}),
        status=200,
        mimetype="application/json"
    )

    return response


@app.route('/metrics')
def metrics():
    connection = get_db_connection()

    payload = {
        "post_count": connection.execute("SELECT COUNT(id) FROM posts").fetchone()[0],
        "db_connection_count": connections
    }
    connection.close()

    response = app.response_class(
        response=json.dumps(payload),
        status=200,
        mimetype="application/json"
    )

    return response


# start the application on port 3111
if __name__ == "__main__":
    # Set logger STDOUT handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)

    # Set logger STDERR handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    logging.basicConfig(format='%(levelname)s:%(name)s:%(asctime)s - %(message)s',
                        level=logging.DEBUG,
                        handlers=[stdout_handler, stderr_handler])

    app.run(host='0.0.0.0', port='3111')
