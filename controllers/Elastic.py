from flask import request
from flask_restplus import reqparse, Resource, Namespace

from config import es, INDEX

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
            return {'Error': 'Make sure you passed parameters'}
        if len(query.split()) > 3:
            match = 3
        else:
            match = len(query.split())
        res = es.search(index=INDEX, body={"query": {"bool": {"should": [
            {
                "match": {
                    "name": {
                        'query': query,
                        'fuzziness': 1

                    }

                }
            },
            {
                "match": {
                    "bio": {
                        'query': query,

                    }

                }
            },
            {
                "match": {
                    "surname": {
                        'query': query,
                        'fuzziness': 1,

                    }
                }
            }
        ],
            "minimum_should_match": match
        }}})
        results = [{
            'name': hit['_source']['name'],
            'surname': hit['_source']['surname'],
            'bio': hit['_source']['bio']

        } for hit in res['hits']['hits'] if 1.4 * hit['_score'] >= res['hits']['max_score']]

        return {"Users": results}
