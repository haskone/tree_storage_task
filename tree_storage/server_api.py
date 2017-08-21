import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask import json
from flask import request

import config
from tree_storage.storage import Storage

app = Flask(__name__)

handler = RotatingFileHandler(config.log_file, maxBytes=config.max_bytes,
                              backupCount=config.backup_count)
handler.setLevel(config.debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

storage = Storage(config.db_url)


@app.route('/nodes', methods=['POST'])
def add_nodes():
    """
    Add specified nodes to the tree.
    Based on storage.Storage.add_nodes. See more for details

    :return: 201 - if all nodes were processed correctly
             400 - in case of incorrect json structure
                   or loop
    """
    input_json = request.get_json()
    app.logger.debug('got json for /nodes: %s', input_json)

    try:
        if storage.is_loop(input_json['nodes']):
            app.logger.warning('got loop with: %s', input_json['nodes'])

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
        # "bad" input
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
    """
    Get part of the tree which contains specified node.
    Based on storage.Storage.get_trees. See more for details

    :param node_id: node id for which need to get a tree
    :return: json with {"trees": <arrays of chains>}
    """
    app.logger.debug('got request for id %s', node_id)

    data = storage.get_trees(node_id=node_id)
    response_data = {'trees': data}
    response = app.response_class(
        response=json.dumps(response_data),
        status=200,
        mimetype='application/json'
    )
    return response
