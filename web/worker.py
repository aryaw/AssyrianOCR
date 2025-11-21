from celery import Celery
import os
from dotenv import load_dotenv
load_dotenv()
broker = os.getenv('CELERY_BROKER_URL','redis://localhost:6379/0')
backend = os.getenv('CELERY_RESULT_BACKEND', broker)
celery_app = Celery('manuscript', broker=broker, backend=backend)
celery_app.conf.update(task_track_started=True, result_extended=True)

@celery_app.task(bind=True)
def train_task(self, epochs=10):
    import subprocess, sys
    env = os.environ.copy()
    env['EPOCHS'] = str(epochs)
    trainer = os.path.join('scripts','train_cnn_classifier.py')
    p = subprocess.Popen([sys.executable, trainer], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out, err = p.communicate()
    return {'code': p.returncode, 'out': out.decode('utf8', errors='ignore'), 'err': err.decode('utf8', errors='ignore')}
