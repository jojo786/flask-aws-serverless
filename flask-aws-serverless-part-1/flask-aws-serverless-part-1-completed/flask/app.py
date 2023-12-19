from flask import Flask, render_template
import os
from boto3.dynamodb.conditions import Key
from boto3 import resource

dynamodb = resource('dynamodb')
posts_table = dynamodb.Table(os.environ["PostsTable"])
app = Flask(__name__)

@app.route('/')
def index():
    posts = ''
    
    try: 
        response = posts_table.scan()
        posts = response['Items']
    except Exception as error:
        print("dynamo scan failed:", error, flush=True) 
              
    return render_template('index.html', posts=posts) 
