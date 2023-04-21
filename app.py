from musicvision import create_app
from musicvision.tasks import start_tasks

app = create_app()
app.debug = True

start_tasks()

app.run()
