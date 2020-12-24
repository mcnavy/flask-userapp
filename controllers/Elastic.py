from flask import request
from flask_restplus import reqparse, Resource, Namespace

from config import es, INDEX

parser = reqparse.RequestParser()
parser.add_argument('name', required=False)
parser.add_argument('surname', required=False)
parser.add_argument('bio', required=False)

api = Namespace('elastic', description='ElasticSearch')


@api.route('/', methods=['GET'])
class SmartGet(Resource):
    @api.expect(parser)
    def get(self):
        match = 0
        name, surname, bio = '', '', ''
        args = request.args
        if 'name' in args.keys():
            match += 1
            name = args['name']
        if 'surname' in args.keys():
            match += 1
            surname = args['surname']
        if 'bio' in args.keys():
            match += 1
            bio = args['bio']
        res = es.search(index=INDEX, body={"query": {"bool": {"should": [
            {
                "match": {
                    "name": {
                        'query': name,
                        'fuzziness': 1

                    }

                }
            },
            {
                "match": {
                    "bio": {
                        'query': bio,

                    }

                }
            },
            {
                "match": {
                    "surname": {
                        'query': surname,
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
