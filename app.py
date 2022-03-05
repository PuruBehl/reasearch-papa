from flask import Flask, render_template, request,url_for,redirect
from werkzeug import secure_filename
import research_papa_python_script as rp
import os
from flask_pymongo import PyMongo
import urllib
from flask_login import LoginManager, UserMixin ,login_user,login_required,current_user,logout_user   
from boto.s3.connection import S3Connection


s3 = S3Connection(os.environ['str1'], os.environ['str2'] , os.environ['str3'])

app = Flask(__name__)

# Setting up the information for the database here
# Getting the uri string
uri_string=s3[0]+urllib.parse.quote(s3[1])+s3[2]

# Adding the pymongo database
mongodb_client = PyMongo(app, uri=uri_string)

# Getting the db
db = mongodb_client.db

@app.route('/')
def simple():
   return render_template('index.html')
   
@app.route('/upload')
def upload_file():
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


      return render_template("uploader.html",dictionary_headings=dic)
   return "No content"
		

@app.route('/login',methods = ["GET","POST"])
def login() :
   error = "Welcome"
   if request.method=="POST":
      data = db.authentication.find_one({"Username":request.form["username"],"Password":request.form['password']})
      if data :
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
      except:
         error = "Please change the username / email since they already exists !!"
      if error=="Welcome" :
         return redirect(url_for('simple'))
   return render_template("signup.html",error=error)




if __name__ == '__main__':
   app.run(debug = True)