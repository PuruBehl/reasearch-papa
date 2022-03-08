from flask import Flask, render_template, request,url_for,redirect,session
from werkzeug import secure_filename
import research_papa_python_script as rp
import os
from flask_pymongo import PyMongo
import urllib
from datetime import timedelta
from flask_login import LoginManager, UserMixin ,login_user,login_required,current_user,logout_user 

app = Flask(__name__)

secret_key = os.environ["str4"]
app.permanent_session_lifetime = timedelta(minutes=300)
app.secret_key = secret_key


# Setting up the information for the database here
# Getting the uri string
uri_string=os.environ['str1']+urllib.parse.quote(os.environ['str2'])+os.environ['str3']




# Adding the pymongo database
mongodb_client = PyMongo(app, uri=uri_string)

# Getting the db
db = mongodb_client.db

@app.route('/')
def simple():
   return render_template('index.html')
   
@app.route('/upload')
def upload_file():
   try :
      if session["user"]:
         pass  
      else :
         return redirect(url_for('login'))
   except :
      return redirect(url_for('login'))
   return render_template('upload.html')
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file2():

   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      path = secure_filename(f.filename)
      text = rp.return_text(path)    
      headings = rp.return_headings(path)
      dic = rp.return_segmented_text(path,with_text=True)
      os.remove(path)

      count=0

      for i in dic :
         count+=1
         dic[i]=[dic[i].encode('utf-8', 'replace').decode(),count]

      hash_code=rp.to_hash(text)

      return render_template("uploader.html",dictionary_headings=dic,hash_code=hash_code)
   return "No content"
		

@app.route('/login',methods = ["GET","POST"])
def login() :
   # session.permanent = True
   error = "Welcome"
   try:
      if session["user"]:
         return redirect(url_for('upload_file'))         
   except:
      pass
   if request.method=="POST":
      data = db.authentication.find_one({"Username":request.form["username"],"Password":request.form['password']})
      if data :
         session["user"]=request.form["username"]
         return redirect(url_for('upload_file'))
      else:
         error = "No such user exists in the database!! Please try to signup !!"
   return render_template("login.html",error=error)


@app.route('/signup',methods = ["GET","POST"])
def signup():
   error = "Welcome"
   if request.method=="POST":
      try:
         db.authentication.insert_one({'Username':request.form["username"],'Password':request.form['password'],
         'Email':request.form['email'],'Name':request.form['name']})
         session["user"]=request.form["username"]
      except:
         error = "Please change the username / email since they already exists !!"
      if error=="Welcome" :
         return redirect(url_for('simple'))
   return render_template("signup.html",error=error)


@app.route('/<variable>/textbox', methods=['GET', 'POST'])
def addtext(variable) :
   if request.method=="POST":
      data=db.research.insert_one({"Review":request.form["review"],"paper_code":variable})
      return redirect(url_for('simple'))
   return render_template('textbox.html')

@app.route('/logout')
def logout():
   session["user"]=None
   return "Logout successfull!!"

if __name__ == '__main__':
   app.run(debug = True)