import cherrypy
#from cherrypy.lib.static import serve_file
import pymupdf
from io import BytesIO
#import tempfile

class WebApp(object):
    @cherrypy.expose
    def index(self):
        return "Welcome to CherryPy!"

    @cherrypy.expose
    def generate(self,wtext="EMPTY"):

        doc = pymupdf.open()

        page = doc.insert_page(-1, # insertion point: end of document
                        text = wtext,
                        fontsize = 11,
                        width = 595, # page dimension: A4 portrait
                        height = 842,
                        fontname = "Helvetica", # default font
                        fontfile = None, # any font file name
                        color = (0, 0, 0))
        
        pdf_bytes = BytesIO()

        doc.save(pdf_bytes)

        doc.close()

        pdf_bytes.seek(0)

        cherrypy.response.headers['Content-Type'] = 'application/pdf'
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="generated_file.pdf"'

        return pdf_bytes.getvalue()
        #return serve_file(pdf_bytes.getvalue(), "application/x-download", "attachment")

cherrypy.config.update({'server.socket_host': '0.0.0.0',    # 127.0.0.1
                        'server.socket_port': 8080,
                       })

cherrypy.quickstart(WebApp())