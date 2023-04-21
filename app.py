from musicvision import create_app

app = create_app()
from musicvision.tasks import start_tasks

start_tasks()

app = create_app()
