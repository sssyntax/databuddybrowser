from serverless_wsgi import handle_request
from app import server

def handler(request, context):
    return handle_request(server, request, context)