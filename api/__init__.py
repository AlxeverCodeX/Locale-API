from flask import Flask
from .config.config import config_dict
from .model.db import connect_to_db
from flask_restx import Api
from .routes.views import state_ns
from .routes.auth import auth_ns
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .routes.views import state_ns, cache
from flask_cors import CORS



def create_app(config=config_dict['development']):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)

    db = connect_to_db()
    jwt = JWTManager(app)

    cache.init_app(app)
    """
    cache = Cache(app,config={
      'CACHE_TYPE':'simple'
    })
    """

    #limiter = Limiter(api, key_func=get_remote_address)

    authorizations = {
      'Bearer Auth':{
        'type':'apiKey',
        'in':'header',
        'name':'authorization',
        'description':''
      }
    }
    api = Api(app, 
              title='Locale API',  
              description='''
                A simple API for getting states and local governments in Nigeria
              ''',
              authorizations=authorizations,
              security='Bearer Auth'
            )
    
    api.add_namespace(state_ns, path='/api/v1')
    api.add_namespace(auth_ns, path='/api/v1')

    state_ns.cache = cache
    

    
    return app
