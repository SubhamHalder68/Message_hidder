from flask import Flask ,render_template,request,redirect,url_for,flash,abort,session,jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.dialects.sqlite
import os.path
import json
from sqlalchemy import text
import math, random
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = 'Subham'

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///message_hiding.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#sender email_password
if os.path.exists('email.json'):
    with open('email.json') as email_file:
        email_data = json.load(email_file)
        sender_email=email_data["sender_email"]
        sender_password=email_data["sender_password"]


app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = sender_email  #sender mail
app.config['MAIL_PASSWORD'] = sender_password #sender password
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = True

mail= Mail(app)
# function to generate password
def generate_password() :
    digits = "0123456789"
    id = ""
    for i in range(4) :
        id += digits[math.floor(random.random() * 10)]
 
    return id
 
db = SQLAlchemy(app)

class Messagedatabase(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    message_o= db.Column(db.String(3000),nullable=False)
    message_en= db.Column(db.String(300),unique=True,nullable=False)
    def __init__(self, id, message_o, message_en):
        self.id = id
        self.message_o = message_o
        self.message_en = message_en
        


@app.route('/')
def index():
    return render_template('index.html',codes=session.keys())

@app.route('/enc',methods = ['POST', 'GET'])
def enc():
    if request.method == 'POST':
        #json_api
        codes= {}
        if os.path.exists('codes.json'):
            with open('codes.json') as codes_file:
                codes = json.load(codes_file)
        if request.form['message_en'] in codes.keys():
            flash('That message encrypted word has already been taken. Please use another name')
            return redirect(url_for('enc'))
        #form
        message_en=request.form['message_en']
        message_o=request.form['message_o']
        email_id=request.form['email_id']
        #part of encrypted word
        some_en=message_en[0]
        for i in range(1,len(message_en)):
            some_en=some_en+'*'

        sql = text('SELECT id FROM messagedatabase')
        check = db.engine.execute(sql)
        Check=[row[0] for row in check]
        
        while True:
            id=generate_password()
            if id not in Check:
                break
        entry=Messagedatabase(id,message_o,message_en)
        #entry=message(id=id,message_o=message_o,message_en=message_en)
        db.session.add(entry)
        db.session.commit()
        #mail_sent
        #sender_mail_is_needed
        msg = Message('Password for encrypted message', sender = sender_email, recipients = [email_id])
        msg.body = "Hello Your Encrypted password:"+id+"for encrypted message:"+some_en+"\n Your will recive your encrypted message via Sender"+"\n to decrypt it visit our website"+url_for('index')
        mail.send(msg)
        #return "mail sent"
        #json_api_add_to_store_email_id
        codes[message_en] = {'email':email_id}
        with open('codes.json','w') as codes_file:
            json.dump(codes,codes_file)
            session[request.form['message_en']]=True
        return render_template('your_encrypt.html', code=request.form['message_en'])

    return render_template('enc.html')
@app.route('/decrypt',methods = ['POST', 'GET'])
def decrypt():
    if request.method == 'POST':
        code=request.form['code']
        password=request.form['password']
        
        sql1 = text('SELECT id FROM messagedatabase WHERE message_en ='+"'"+code+"'")
        pwCheck = db.engine.execute(sql1)
        pwCheck=[row[0] for row in pwCheck]
        pw=str(pwCheck[0])
        
        if password == pw:
            sql2=text('SELECT message_o FROM messagedatabase WHERE id ='+password)
            showm=db.engine.execute(sql2)
            show=[row[0] for row in showm]
            return render_template('messageshow.html', showm=show[0])
        else:
            flash("Password does not matched")
            return render_template('decrypt.html')

    return render_template('decrypt.html')

@app.route('/your_encrypt',methods=['GET','POST'])
def your_url():
    if request.method == 'POST':
        urls= {}
        if os.path.exists('urls.json'):
            with open('urls.json') as urls_file:
                urls = json.load(urls_file)
        if request.form['code'] in urls.keys():
            flash('That short name has already been taken. Please use another name')
            return redirect(url_for('index'))

        urls[request.form['code']] = {'url':request.form['url']}
        with open('urls.json','w') as url_file:
            json.dump(urls,url_file)
            session[request.form['code']]=True
        return render_template('your_url.html', code=request.form['code'])
    else:
        return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('pagenotfound.html'),404

@app.route('/api')
def session_api():
    return jsonify(list(session.keys()))

if __name__=="__main__":
    app.run (debug=True)