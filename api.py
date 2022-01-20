
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.core import ActsExtractor
import os, uuid, pandas as pd

PREFIX = '/dash/api'

app = Flask(__name__)
cors = CORS(app, resources={r"/dash/api/*": {"origins": "*"}})

@app.route(f'{PREFIX}/extract_entity', methods=['POST'])
@cross_origin()
def extract_entity():
    name = uuid.uuid4().hex
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
            for index, _ in enumerate(df_list):
                del df_list[index][0]

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
    name = uuid.uuid4().hex
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

    for act_name in acts_dfs:
        df = acts_dfs[act_name]
        response[act_name] = df.acts_str

    return jsonify(response)

@app.route(f'{PREFIX}/extract_all', methods=['POST'])
@cross_origin()
def extract_all():
    name = uuid.uuid4().hex
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

    for act_name in acts_dfs:
        acts = acts_dfs[act_name]
        df = acts.data_frame

        columns = df.columns.tolist()
        columns = columns[1:]

        entities = df.where(pd.notnull(df), None) # Remove NaN
        entities = entities.values.tolist()
        if len(entities) > 0:
            for index, _ in enumerate(entities):
                del entities[index][0]
        
        content = []
        for index, entity in enumerate(entities):
            content.append({
                'entities': entity,
                'text': acts.acts_str[index],
                'file': f.filename,
            })

        if len(content) > 0:
            response[act_name] = {
                'content': content,
                'title': act_name,
                'columns': columns
            }

    return response

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)