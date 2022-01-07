
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.core import ActsExtractor
import os, pandas as pd

PREFIX = '/dash/api'

app = Flask(__name__)
cors = CORS(app, resources={r"/dash/api/*": {"origins": "*"}})
# app.config['CORS_HEADERS'] = 'Content-Type'

@app.route(f'{PREFIX}/extract_entity', methods=['POST'])
@cross_origin()
def extract_entity():
    type = 'ner'

    f = request.files['file']
    f.save(f.filename)

    if 'pdf' in f.filename:
        temp_text = open('tmp_txt.txt', 'w+')
        text = ContentExtractor.extract_text(f.filename)
        temp_text.write(text)
        temp_text.close()

        acts_dfs = ActsExtractor.get_all_df('tmp_txt.txt', type)
    
        try:
            os.remove(f.filename)
            os.remove('tmp_txt.txt')
        except:
            pass

        response = []
        for act_name in acts_dfs:
            df = acts_dfs[act_name]
            columns = df.columns.tolist()
            columns = columns[1:]
            df = df.where(pd.notnull(df), None) # Remove NaN
            df_list = df.values.tolist()
            if len(df_list) > 0:
                for item in df_list:
                    del item[0]
                response.append({
                    'content': df_list,
                    'title': act_name,
                    'columns': columns
                })

        return jsonify(response)
        
    return 'Not a pdf file', 400

@app.route(f'{PREFIX}/extract_acts', methods=['POST'])
@cross_origin()
def extract_acts():
    f = request.files['file']
    f.save(f.filename)

    if 'pdf' in f.filename:
        temp_text = open('tmp_txt.txt', 'w+')
        text = ContentExtractor.extract_text(f.filename)
        temp_text.write(text)
        temp_text.close()

        acts_dfs = ActsExtractor.get_all_obj('tmp_txt.txt', 'ner')

        try:
            os.remove(f.filename)
            os.remove('tmp_txt.txt')
        except FileNotFoundError:
            print('Erro na remoção de uma dos arquivos. Continuando normalmente...')

        response = {}

        print(acts_dfs)

        for act_name in acts_dfs:
            print(act_name)
            df = acts_dfs[act_name]
            response[act_name] = df.acts_str
        
        for act in response:
            print(act, len(response[act]))

        return jsonify(response)
        
    return 'Not a pdf file', 400

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
