from flask import Flask, render_template, request, url_for, flash, redirect
import os
from boto3.dynamodb.conditions import Key
from boto3 import resource
from werkzeug.exceptions import abort
import boto3
from botocore.config import Config

DBClusterArn = os.environ['DBClusterArn']
DBName = os.environ['DBName']
SecretArn = os.environ['SecretArn']
my_config = Config(
        region_name = os.environ['AWS_REGION'])
client = boto3.client('rds-data', config=my_config)

app = Flask(__name__)
app.config['SECRET_KEY'] = '454543gtgdfgdfgfdgfd'

@app.route('/')
def index():
    posts = []

    response = client.execute_statement(
        resourceArn=DBClusterArn,
        secretArn=SecretArn,
        database=DBName,
        sql="""SELECT * FROM posts"""
    )

    for record in response['records']:
        posts.append({
            'id': record[0]['longValue'],
            'created': record[1]['stringValue'],
            'title': record[2]['stringValue'],
            'content': record[3]['stringValue']
        })

    return render_template('index.html', posts=posts) 

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    
    return render_template('post.html', post=post)

def get_post(post_id):
    post = {}
    
    response = client.execute_statement(
        resourceArn=DBClusterArn,
        secretArn=SecretArn,
        database=DBName,
        sql="""SELECT * FROM posts WHERE id = :id""",
        parameters=[
                {
                'name':'id', 
                'value':{'longValue':post_id}
                }
            ] 
    )
    
    for record in response['records']:
        post['id'] = record[0]['longValue']
        post['created'] = record[1]['stringValue']
        post['title'] = record[2]['stringValue']
        post['content'] = record[3]['stringValue']
    
    if len(post) == 0:
        abort(404)
    
    return post

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']
        
        if not title:
            flash('Title is required!')
        else:
            response = client.execute_statement(
                resourceArn=DBClusterArn,
                secretArn=SecretArn,
                database=DBName,
                sql="""
                INSERT INTO posts (title, content) 
                VALUES (:title, :content)
                """,
                parameters=[
                        {
                        'name':'title', 
                        'value':{'stringValue':title}
                        },
                        {
                        'name':'content', 
                        'value':{'stringValue':content}
                        }
                    ] 
            ) 
                  
            return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            response = client.execute_statement(
                resourceArn=DBClusterArn,
                secretArn=SecretArn,
                database=DBName,
                sql="""
                UPDATE posts SET title = :title, content = :content
                WHERE id = :id 
                """,
                parameters=[
                    {
                        'name':'title', 
                        'value':{'stringValue':title}
                        },
                        {
                        'name':'content', 
                        'value':{'stringValue':content}
                        },
                        {
                        'name':'id', 
                        'value':{'longValue':id}
                        }
                    ] 
            ) 

            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)

    response = client.execute_statement(
        resourceArn=DBClusterArn,
        secretArn=SecretArn,
        database=DBName,
        sql="""DELETE FROM posts WHERE id = :id""",
        parameters=[
                {
                'name':'id', 
                'value':{'longValue':id}
                }
            ] 
    ) 
        
    return redirect(url_for('index'))