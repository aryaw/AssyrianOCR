import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, "scripts")

if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import cv2
from scripts.auto_cluster_cuneiform import auto_cluster_tablet, export_clustered_dataset
def cluster_image(image_path, k=8):
    img = cv2.imread(image_path)
    if img is None:
        return {'error':'failed to read image'}
    rois, cluster_ids, _ = auto_cluster_tablet(img, k)
    boxes=[]
    rows=[]
    for i, ((x0,y0,x1,y1,roi), cid) in enumerate(zip(rois, cluster_ids)):
        boxes.append([int(x0),int(y0),int(x1),int(y1),1.0])
        rows.append({'id':i,'cluster':int(cid),'x0':int(x0),'y0':int(y0),'x1':int(x1),'y1':int(y1)})
    return {'image': image_path, 'boxes': boxes, 'cluster_ids': cluster_ids.tolist() if hasattr(cluster_ids,'tolist') else list(cluster_ids), 'rows': rows}

def export_clusters(image_path, k=8, out='data/cnn_auto/train'):
    img = cv2.imread(image_path)
    rois, cluster_ids, _ = auto_cluster_tablet(img, k)
    export_clustered_dataset(rois, cluster_ids, out=out)
    return out
