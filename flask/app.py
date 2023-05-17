from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
from redis import Redis
import pylibmc
from flask_sqlalchemy import SQLAlchemy
import os

SESSION_TYPE = os.environ.get('SESSION_TYPE')
IP = os.environ.get('DIR_IP')
# Create the Flask application
app = Flask(__name__, template_folder="templates")
app.secret_key = 'secret key'
app.config['SESSION_TYPE'] = SESSION_TYPE

if SESSION_TYPE == 'redis':
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = Redis(host=IP, port=6379)

if SESSION_TYPE == 'memcached':
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_MEMCACHED'] = pylibmc.Client([IP],
                                                     binary=True,
                                                     behaviors={"tcp_nodelay": True, "ketama": True})

if SESSION_TYPE == 'filesystem':
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = "/tmp/flask_session"

if SESSION_TYPE == 'sqlalchemy':
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@' + IP + '/SO_DIS'
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
    db = SQLAlchemy(app)
    db.create_all()
    db.session.commit()
    app.config['SESSION_SQLALCHEMY'] = db
# Create and initialize the Flask-Session object AFTER `app` has been configured
Session(app)

@app.route("/")
@app.route("/home")
def home():
    card = session.get('card', [])
    total = session.get('total', 0)
    count = session.get('count', 0)
    return render_template("home.html", products = card, total = total, count = count)

@app.route("/clear", methods = ['GET'])
def clearCard():
    session.clear()
    return redirect(url_for('home'))

@app.route('/add',methods = ['GET'])
def login():
    card = session.get('card', [])
    card.insert(0, {
        'name':request.args.get('name'),
        'price':float(request.args.get('price'))
    })
    session["total"] = float("{:.2f}".format(sum([i['price'] for i in card])))
    session["count"] = len(card)
    session['card'] = card
    return redirect(url_for('home'))
if __name__ == "__main__":
    print("PORT: ", os.environ.get('PORT'))
    print("DIR_IP: ", os.environ.get('DIR_IP'))
    print("SESSION_TYPE: ", os.environ.get('SESSION_TYPE'))

    app.run(debug= True, host='127.0.0.1', port=os.environ.get('PORT'))