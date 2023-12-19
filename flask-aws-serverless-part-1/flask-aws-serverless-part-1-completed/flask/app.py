from flask import Flask, render_template, request, url_for, flash, redirect
import os
from boto3.dynamodb.conditions import Key
from boto3 import resource
from werkzeug.exceptions import abort
import uuid
from datetime import datetime
from decimal import Decimal 

dynamodb = resource('dynamodb')
posts_table = dynamodb.Table(os.environ["PostsTable"])
app = Flask(__name__)
app.config['SECRET_KEY'] = '454543gtgdfgdfgfdgfd'

@app.route('/')
def index():
    posts = ''
    
    try: 
        response = posts_table.scan()
        posts = response['Items']
    except Exception as error:
        print("dynamo scan failed:", error, flush=True) 
              
    return render_template('index.html', posts=posts) 

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    
    return render_template('post.html', post=post)

def get_post(post_id):
    try:
        response = posts_table.get_item(Key={'id': post_id})
        post = response['Item']
    except Exception as error:
        print("dynamo get post failed:", error, flush=True) 
        abort(404)

    return post

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']
        created = str(datetime.now())
        id = int(datetime.now().timestamp())
        
        if not title:
            flash('Title is required!')
        else:
            try: 
                #insert new post into dynamodb
                posts_table.put_item(
                    Item={
                        'id': id,
                        'title': title,
                        'content': content,
                        'created': created
                        }
                )
            except Exception as error:
                print("dynamo PUT failed:", error, flush=True) 
                  
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
            try:
                    posts_table.update_item(
                    Key={
                        'id': id
                        },
                        UpdateExpression="set title = :title, content = :content",
                        ExpressionAttributeValues={
                            ':title': title,
                            ':content': content
                            }
                )
            except Exception as error:
                print("dynamo update failed:", error, flush=True) 
                       
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)

    try:
        posts_table.delete_item(
            Key={
                'id': id
                }
        )
        flash('"{}" was successfully deleted!'.format(post['title']))
    except Exception as error:
        print("dynamo delete failed:", error, flush=True)  
        
    
    return redirect(url_for('index'))