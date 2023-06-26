from flask_restx import Namespace, Resource
from ..model.db import connect_to_db
from flask import jsonify, Response,render_template
from http import HTTPStatus
from bson import json_util
from bson.objectid import ObjectId
from flask_limiter import Limiter
from ratelimit import limits
from flask import Flask
from flask_caching import Cache



cache = Cache(config={
      'CACHE_TYPE':'simple'
    })


#app = Flask(__name__, static_url_path='/static')

state_ns = Namespace('state', description='Namespace for State')



 # Max  calls per day
#@limits(calls=2, period=86400)
def get_regions():
        database = connect_to_db()
        regions = database.locale.regions

        data = list(regions.find())

        for item in data:
            item['_id'] = str(ObjectId(item['_id']))
        
        return data
       


#   Serialize state data
#@limits(calls=2, period=86400)
def get_states(): 
    database = connect_to_db()
    states = database.locale.data

    data = list(states.find())

    for item in data:
        item['_id'] = str(ObjectId(item['_id']))

    return data




@state_ns.route('/states/<string:state_id>')
class State(Resource):
    @limits(calls=2, period=86400)
    @cache.cached(timeout=3600)
    def get(self, state_id):
        """
        Get a single state
        """
        try:
            database = connect_to_db()
            states = database.locale.data

            # Check if the state_id is a valid ObjectId
            if not ObjectId.is_valid(state_id):
                return {'message': 'Invalid state_id'}, HTTPStatus.BAD_REQUEST

            state = states.find_one({'_id': ObjectId(state_id)})

            if state:
                state['_id'] = str(state['_id'])
                response = jsonify(state)
                return Response(response.get_data(), status=HTTPStatus.OK, mimetype='application/json')
            else:
                return {'message': 'State not found'}, HTTPStatus.NOT_FOUND
        
        except Exception as e:
            print(e)
            return {'message': 'An error occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR


@state_ns.route('/regions/<string:region_id>')
class Region(Resource):
    @limits(calls=2, period=86400)
    @cache.cached(timeout=3600)
    def get(self, region_id):
        """
            Get a single region
        """
        try:
            database = connect_to_db()
            regions = database.locale.regions

            geo_political_zone = regions.find_one({'_id': ObjectId(region_id)})

            geo_political_zone['_id'] = str(ObjectId(geo_political_zone['_id']))

            response = jsonify(geo_political_zone)

            return Response(response.get_data(), status=HTTPStatus.OK, mimetype='application/json')
        
        except Exception as e:
            print(e)

            return {'message': 'An error occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR
        
        except Exception as e:
            print(e)
            return {'message': 'An error occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR
        


#   Serialize lga data
def get_lgas():
    database = connect_to_db()
    lgas = database.locale.local_governments

    data = list(lgas.find())

    # for item in data:
    #     item['_id'] = str(ObjectId(item['_id']))
    #     item['state_id'] = str(ObjectId(item['state_id']))

    return data

 
@state_ns.route('/regions')
class Regions(Resource): 
    @limits(calls=2, period=86400)
    @cache.cached(timeout=3600) 
    def get(self):
        """
            Get all regions
        """
        #try:
        data = get_regions()

        response = jsonify(data)
            
        return Response(response.get_data(), status=HTTPStatus.OK, mimetype='application/json')
        
        #except Exception as e:
            #print(e)

        return {'message': 'An error occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR
       
        


@state_ns.route('/lgas')
class Lgas(Resource):
    @limits(calls=2, period=86400)
    @cache.cached(timeout=3600) 
    def get(self):
        """
            Get all lgas
        """
        try:
            data = get_lgas()
            json_data = json_util.dumps(data)
            lgas = json_util.loads(json_data)

            for item in lgas:
                item['_id'] = str(ObjectId(item['_id']))
                item['state_id'] = str(ObjectId(item['state_id']))

            response = jsonify(lgas)

            return Response(response.get_data(), status=HTTPStatus.OK, mimetype='application/json')
        
        except Exception as e:
            print(e)

            return {'message': 'An error occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR


@state_ns.route('/lgas/<string:state_id>')
class Lga(Resource):
    @limits(calls=2, period=86400)
    @cache.cached(timeout=3600)
    def get(self, state_id):
        """
            Get all lgas in a state
        """
        try:
            database = connect_to_db()
            lgas = database.locale.local_governments

            data = list(lgas.find({'state_id': ObjectId(state_id)}))

            for item in data:
                item['_id'] = str(ObjectId(item['_id']))
                item['state_id'] = str(ObjectId(item['state_id']))

            response = jsonify(data)

            return Response(response.get_data(), status=HTTPStatus.OK, mimetype='application/json')
        
        except Exception as e:
            print(e)

            return {'message': 'An error occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR

@state_ns.route('/states')
class States(Resource):
    @limits(calls=2, period=86400)
    @cache.cached(timeout=3600)
    def get(self):
        """
            Get all states
        """
        try:
            data = get_states()

            response = jsonify(data)

            return Response(response.get_data(), status=HTTPStatus.OK, mimetype='application/json')
        
        except Exception as e:
            print(e)

            return {'message': 'An error occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR




@state_ns.route('/search/<string:query>')
class Search(Resource):
    def get(self, query):
        """
        Search for a state or LGA
        """
        try:
            database = connect_to_db()
            states = database.locale.data
            lgas = database.locale.local_governments
            regions = database.locale.regions

            # Search for the state
            state = states.find_one({'state': query})
            lga = lgas.find_one({'lga': query})
            region = regions.find_one({'name': query})
            if state:
                state['_id'] = str(ObjectId(state['_id']))
                return state, HTTPStatus.OK

            # Search for the LGA
            
            elif lga:
                lga['_id'] = str(ObjectId(lga['_id']))
                lga['state_id'] = str(ObjectId(lga['state_id']))
                return lga, HTTPStatus.OK

            # Search for the region
            
            elif region:
                region['_id'] = str(ObjectId(region['_id']))
                return region, HTTPStatus.OK

            # No results found
            else:
                return {'message': 'No results found'}, HTTPStatus.NOT_FOUND

        except Exception as e:
            print(e)
            return {'message': 'An error occurred'}, HTTPStatus.INTERNAL_SERVER_ERROR
