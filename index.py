import cherrypy

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return "Welcome to CherryPy!"


cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 80,
                       })

cherrypy.quickstart(HelloWorld())