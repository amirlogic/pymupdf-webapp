import cherrypy

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return "Welcome to CherryPy!"

cherrypy.quickstart(HelloWorld())