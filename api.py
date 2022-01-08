
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.core import ActsExtractor
import os, time, pandas as pd

PREFIX = '/dash/api'

app = Flask(__name__)
cors = CORS(app, resources={r"/dash/api/*": {"origins": "*"}})

@app.route(f'{PREFIX}/extract_entity', methods=['POST'])
@cross_origin()
def extract_entity():
    name = request.remote_addr + '_' + str(int(time.time()))
    f = request.files['file']

    if not f.filename.endswith('.pdf'):
        return 'Not a pdf file', 400

    f.save(name + '.pdf')

    temp_text = open(name + '.txt', 'w+')
    text = ContentExtractor.extract_text(name + '.pdf')
    temp_text.write(text)
    temp_text.close()

    acts_dfs = ActsExtractor.get_all_df(name + '.txt', 'ner')

    try:
        os.remove(name + '.pdf')
        os.remove(name + '.txt')
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
            for i, item in enumerate(df_list):
                del item[0]

            for index, row in enumerate(df_list):
                list_null = [x for x in row if x is None or isinstance(x, list)]
                if len(list_null) == 0:
                    del df_list[index]

            response.append({
                'content': df_list,
                'title': act_name,
                'columns': columns
            })
        response = sorted(response, key=lambda k: k['title'])

    return jsonify(response)

@app.route(f'{PREFIX}/extract_acts', methods=['POST'])
@cross_origin()
def extract_acts():
    name = request.remote_addr + '_' + str(int(time.time()))
    f = request.files['file']

    if not f.filename.endswith('.pdf'):
        return 'Not a pdf file', 400

    f.save(name + '.pdf')

    temp_text = open(name + '.txt', 'w+')
    text = ContentExtractor.extract_text(name + '.pdf')
    temp_text.write(text)
    temp_text.close()

    acts_dfs = ActsExtractor.get_all_obj(name + '.txt', 'ner')

    try:
        os.remove(name + '.pdf')
        os.remove(name + '.txt')
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

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
