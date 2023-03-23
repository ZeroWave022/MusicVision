from musicvision import create_app
from livereload import Server

app = create_app()
app.debug = True

livereload_server = Server(app.wsgi_app)
livereload_server.watch(".")
livereload_server.serve()
