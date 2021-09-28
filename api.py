from flask import Flask, request
from flask_cors import CORS, cross_origin
from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.core import ActsExtractor
import json, os

app = Flask(__name__)
cors = CORS(app, CORS_ORIGINS="localhost:5000")
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/extract_content', methods=['POST'])
@cross_origin()
def extract_content():
    try:
        type = request.form['type']
    except:
        type = 'regex'
    
    f = request.files['file']
    f.save(f.filename)

    if 'pdf' in f.filename:
        temp_text = open('tmp_txt.txt', 'w+')
        text = ContentExtractor.extract_text(f.filename)
        temp_text.write(text)

        acts_dfs = ActsExtractor.get_all_df('tmp_txt.txt', type)

        os.remove(f.filename)
        os.remove('tmp_txt.txt')

        return_list = []
        for act_name in acts_dfs:
            df = acts_dfs[act_name]
            for list_ in df.values.tolist():
                return_list = return_list + list_

        return json.dumps(return_list)
        
    return 'Not a pdf file', 400

if __name__ == '__main__':
    app.run(debug=True)
