from flask import Flask, render_template, url_for, request
import re
import nltk
from nltk.stem.porter import PorterStemmer
import os
import pickle
import pandas as pd
from numpy import genfromtxt
import werkzeug
app = Flask(__name__)


@app.route('/upload')
def upload_file():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      data= genfromtxt(os.path.abspath(f.filename) , delimiter=',')
      graph = pygal.Line()

      if data.shape[1]==0:
          graph.add('Data', data)
      else:
          graph.add('Data', data[1,:])

      graph_data = graph.render_data_uri()
      return render_template("upload.html", graph_data = graph_data)


if __name__ == '__main__':
    app.run(debug=False)
