from flask import Flask, render_template, request
from dodfminer.extract.pure.core import ContentExtractor
from dodfminer.extract.polished.core import ActsExtractor
import json, os

app = Flask(__name__)

files_list = []

@app.route('/extract_content', methods=['POST'])
def extract_content():
    f = request.files['file']
    f.save(f.filename)

    if 'pdf' in f.filename:
        temp_text = open('tmp_txt.txt', 'w+')
        text = ContentExtractor.extract_text("contrato1.pdf")
        temp_text.write(text)
    
        acts_dfs = ActsExtractor.get_all_df('tmp_txt.txt', 'regex')

        return_list = []
        for act_name in acts_dfs:
            df = acts_dfs[act_name]
            for list in df.values.tolist():
                return_list = return_list + list

        return json.dumps(return_list)
        
    return 'Not a pdf file', 400

if __name__ == '__main__':
    app.run(debug=True)
