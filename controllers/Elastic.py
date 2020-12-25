from flask import request
from flask_restplus import reqparse, Resource, Namespace

from config import es, INDEX, SEARCHABLE_ELASTIC_FIELDS

parser = reqparse.RequestParser()
parser.add_argument('query', required=False)

api = Namespace('elastic', description='ElasticSearch')


@api.route('/', methods=['GET'])
class SmartGet(Resource):
    @api.expect(parser)
    def get(self):

        query = ''
        args = request.args
        if 'query' in args.keys():
            query = args['query']
        else:
            return {'code': 400, 'message': 'Error, make sure you passed query'}
        match = min(len(query.split()), len(SEARCHABLE_ELASTIC_FIELDS))

        es_param = [{
            "match": {
                field: {
                    "query": query,
                    "fuzziness": 1
                }
            }
        } for field in SEARCHABLE_ELASTIC_FIELDS]

        res = es.search(index=INDEX, body={"query": {"bool": {"should": es_param,
                                                              "minimum_should_match": match
                                                              }}})
        results = [{
            'name': hit['_source']['name'],
            'surname': hit['_source']['surname'],
            'bio': hit['_source']['bio']

        } for hit in res['hits']['hits'] if 1.4 * hit['_score'] >= res['hits']['max_score']]

        return {"Users": results}
