from flask import Flask, render_template, request
from werkzeug import secure_filename
import research_papa_python_script as rp
import os

app = Flask(__name__)

@app.route('/')
def simple():
   return "Hellow world"
   
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

      for i in dic :
         dic[i]=dic[i].encode('utf-8', 'replace').decode()

      return render_template("uploader.html",dictionary_headings=dic)
   return "No content"
		
if __name__ == '__main__':
   app.run(debug = True)