from flask import Flask, request, render_template, redirect
from controller import save_image, search

app = Flask(__name__, static_url_path="/data", static_folder='data')

@app.route('/', methods=['GET', 'POST'])
@app.route('/similar/<path:path>', methods=['GET', 'POST'])
def index(path=None):
  if request.method == 'POST':
    key = save_image(request.files['image'])
    return redirect('/similar/' + key)

  if path is None:
    return render_template('index.html')
  
  if path == 'random':
    import os, glob, random
    path = os.path.splitext(os.path.basename(random.sample(glob.glob(os.path.join(os.path.dirname(__file__), 'data/images/processed/*.jpg')), 1)[0]))[0]
  
  results = search(path)
  return render_template('index.html', query=path, results=results)

if __name__=="__main__":
    app.run(host='0.0.0.0', port=4005, threaded=True)
