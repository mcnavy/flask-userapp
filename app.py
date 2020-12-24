import os
from config import app, api
from controllers.User import api as user_api
from controllers.Event import api as event_api
from controllers.Elastic import api as elastic_api

api.add_namespace(user_api, path='/user')
api.add_namespace(event_api, path='/event')
api.add_namespace(elastic_api,path='/smart_get')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
