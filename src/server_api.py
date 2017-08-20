import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask import json
from flask import request

import config
from storage import Storage

app = Flask(__name__)
storage = Storage(config.db_url)


@app.route('/nodes', methods=['POST'])
def add_nodes():
    input_json = request.json
    app.logger.info('got json for /nodes: %s', input_json)

    try:
        if storage.is_loop(input_json['nodes']):
            # in case of any loop chain - return 400
            # and ignore other values
            data = {"error": "Loop relations not allowed"}
            code = 400
        else:
            data = {}
            code = 201
            for node in input_json['nodes']:
                storage.add_nodes(node['id'], node['parent'])
    except KeyError as ke:
        app.logger.error('got error: %s', str(ke))

        # Despite this response is not a part of
        # the original requirements,
        # we need to answer something in case of
        # bad input
        data = {"error": "Broken input"}
        code = 400

    response = app.response_class(
        response=json.dumps(data),
        status=code,
        mimetype='application/json'
    )
    return response


@app.route('/trees/<node_id>', methods=['GET'])
def get_trees(node_id):
    app.logger.info('got request for id %s', node_id)
    data = storage.get_trees(node_id=node_id)
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    handler = RotatingFileHandler(config.log_file, maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.run()
