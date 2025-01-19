import cherrypy
#from cherrypy.lib.static import serve_file
import pymupdf
from io import BytesIO

import base64

from jinja2 import Environment, FileSystemLoader, select_autoescape

jenv = Environment(
    loader=FileSystemLoader(''),
    autoescape=select_autoescape()
)

class WebApp(object):
    @cherrypy.expose
    def index(self):
        htfile = open('home.html','r')
        return htfile

    @cherrypy.expose
    def upload(self):

        upload_template = jenv.get_template("upload.html")
        #htfile = open('upload.html','r')
        return upload_template.render()

    @cherrypy.expose
    def getfile(self,input,mode):
        try:
            
            print("File upload processing...")
            print("Content length:",cherrypy.serving.request.headers['Content-length'])
            print("Content type:",cherrypy.serving.request.headers['Content-type'])

            if not input.file:
                return "No file uploaded or invalid file."

            print("Filename: ", input.filename)

            upfile_bytes = BytesIO(input.file.read())

            upfile_bytes.seek(0)

            doc = pymupdf.open(stream=upfile_bytes)

            if(mode=="meta"):

                info_template = jenv.get_template("fileinfo.html")

                pgCount = doc.page_count

                metaData = doc.metadata

                metaData['pgCount'] = pgCount

                print("Metadata: ", metaData)

                print("Pages: ", pgCount)

                doc.close()
                

                return info_template.render(metaData)   

            elif(mode=="text"):

                output = ""

                for page in doc: # iterate the document pages
                    text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
                    print("Page text: ",text)
                    output += str(text) # write text of page

                doc.close()

                return "Extracting text"+output

            elif(mode=="images"):

                lenXREF = doc.xref_length()

                imgcount = 0

                html_content = ""

                ximages = []

                for xref in range(1, lenXREF):
    
                    if(doc.xref_get_key(xref, "Subtype")[1] == "/Image"):

                        imgcount += 1

                        imgdata = doc.extract_image(xref)

                        base64_bytes = base64.b64encode(imgdata['image'])

                        base64_string = base64_bytes.decode("ascii")


                        img_header = 'Image xref='+str(xref)+' ext: '+ imgdata['ext'] +' width: '+ str(imgdata['width']) +' height: '+ str(imgdata['height'])

                        html_content += '<img src="data:image/' + imgdata['ext'] + ';base64,' + base64_string + '" alt="xref' + str(xref) + '" />'  


                        ximages.append({ "img_header":img_header, "ext":imgdata['ext'], "base64":base64_string })
        

                payload_template = jenv.get_template("xref_images.html")

                doc.close()

                return payload_template.render({"payload":ximages})   

            elif(mode=="tables"):

                html = "<html><body>"

                for page in doc:
                    tbls = page.find_tables()
                    print("Tables found: ",len(tbls.tables))
                    html += "<div>"
                    if(len(tbls.tables)>0):
                        print("This page contains tables")
                        for wt in tbls.tables:
                            cr = wt.extract()
                            print(cr)
                            html += "<div>Here is a table:<table style=\"margin:50px\">"
                            #html += "<tr><td>" + type(wt) + "</td></tr>"
                            for r in cr:
                                
                                html += "<tr>"
                                html += "<td>" + str(r[0]) + "</td><td>" + str(r[1]) + "</td>"
                                html += "</tr>"

                            html += "</table><div>"
                    html += "</div>"    

                html += "</body></html>"

                doc.close()

                return html

            else:
                return "Unknown action"
           
        except:
            print("Error! mode ",mode)
            return "Error!" 

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