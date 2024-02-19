# app.py
from flask import Flask, Response
from flask_cors import CORS
from flask_restful import Resource, Api
import datastats_service
from decouple import config

app = Flask(__name__)
CORS(app)
api = Api(app)

# RESOURCE CLASSES
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'This is a Flask API !'}

class GetTop5(Resource):
    def get(self):
        json_data = datastats_service.get_top_5_data()
        return Response(response=json_data, status=200, content_type='application/json')

class GetOfferEvolution(Resource):
    def get(self):
        json_data = datastats_service.get_offer_evolution_data()
        return Response(response=json_data, status=200, content_type='application/json')

class GetTopSkills(Resource):
    def get(self, job_search=None):
        json_data = datastats_service.get_top_skills_data(job_search)
        return Response(response=json_data, status=200, content_type='application/json')

class GetTop5Jobs(Resource):
    def get(self):
        json_data = datastats_service.get_top_5_jobs()
        return Response(response=json_data, status=200, content_type='application/json')

# ROUTES
api.add_resource(HelloWorld, '/')
api.add_resource(GetTop5, '/top_5')
api.add_resource(GetOfferEvolution, '/offer_evolution')
api.add_resource(GetTopSkills, '/top_skills', '/top_skills/<string:job_search>')
api.add_resource(GetTop5Jobs, '/top_5_jobs')

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=config('DEBUG'))