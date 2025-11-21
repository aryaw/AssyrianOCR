import subprocess, sys, os
def train_from_cluster_dir(epochs=10):
    trainer = os.path.join('scripts','train_cnn_classifier.py')
    if not os.path.exists(trainer):
        return {'error':'trainer missing'}
    env = os.environ.copy()
    env['EPOCHS']=str(epochs)
    p = subprocess.Popen([sys.executable, trainer], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out, err = p.communicate()
    if p.returncode != 0:
        return {'ok': False, 'stderr': err.decode('utf8', errors='ignore')}
    return {'ok': True, 'stdout': out.decode('utf8', errors='ignore')}
