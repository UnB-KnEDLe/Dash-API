from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.core import ActsExtractor
import json, os, pandas as pd

app = Flask(__name__)
cors = CORS(app, CORS_ORIGINS="localhost:5000")
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/extract_content', methods=['POST'])
@cross_origin()
def extract_content():
    type = 'ner'

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
            df = df.where(pd.notnull(df), None) # Remove NaN
            df_list = df.values.tolist()
            if len(df_list) > 0:
                for item in df_list:
                    del item[0]
                return_list.append({
                    'content': df_list,
                    'title': act_name
                })

        return jsonify(return_list)
        
    return 'Not a pdf file', 400

if __name__ == '__main__':
    app.run(debug=True)
