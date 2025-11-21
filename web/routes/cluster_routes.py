from flask import Blueprint, request, jsonify
from ..services.clustering_service import cluster_image, export_clusters
cluster_bp = Blueprint('cluster_bp', __name__)

@cluster_bp.route('/run', methods=['POST'])
def run_cluster():
    import os, csv, json
    from datetime import datetime
    from PIL import Image, ImageDraw

    data = request.get_json() or {}

    image_paths = data.get("images")
    k = int(data.get("k", 8))

    if not image_paths:
        return jsonify({"error": "missing images"}), 400

    if isinstance(image_paths, str):
        image_paths = [image_paths]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    out_csv = "data/output/csv"
    out_json = "data/output/json"
    out_clustered = "data/output/img_clustered"
    out_crops = "data/output/crops"

    for d in [out_csv, out_json, out_clustered, out_crops]:
        os.makedirs(d, exist_ok=True)

    results = []
    for img_path in image_paths:

        base = os.path.splitext(os.path.basename(img_path))[0]

        res = cluster_image(img_path, k)

        if "error" in res:
            results.append({
                "image": img_path,
                "error": res["error"]
            })
            continue

        rows = res.get("rows", [])
        boxes = res.get("boxes", [])
        cluster_ids = res.get("cluster_ids", [])

        csv_path = os.path.join(out_csv, f"{base}_cluster_{timestamp}.csv")
        json_path = os.path.join(out_json, f"{base}_cluster_{timestamp}.json")
        clustered_path = os.path.join(out_clustered, f"{base}_clustered_{timestamp}.png")

        if rows:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(rows[0].keys())
                for r in rows:
                    writer.writerow(r.values())

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)

        web_clustered_url = None
        try:
            img = Image.open(img_path).convert("RGB")
            draw = ImageDraw.Draw(img)

            def cid_to_color(cid):
                return ((cid * 97) % 255, (cid * 53) % 255, (cid * 11) % 255)

            for b, cid in zip(boxes, cluster_ids):
                x1, y1, x2, y2 = b[:4]

                color = cid_to_color(cid)
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                draw.text((x1 + 4, y1 + 4), f"C{cid}", fill=color)

            img.save(clustered_path)

            web_clustered_url = "data/output/img_clustered/" + os.path.basename(clustered_path)

        except Exception as e:
            web_clustered_url = None
            res["clustered_image_error"] = str(e)

        crop_dir = os.path.join(out_crops, base)
        os.makedirs(crop_dir, exist_ok=True)

        crop_paths = []

        try:
            img_cv = Image.open(img_path).convert("RGB")

            for i, (b, cid) in enumerate(zip(boxes, cluster_ids)):
                x1, y1, x2, y2 = b[:4]
                crop = img_cv.crop((x1, y1, x2, y2))

                crop_name = f"{base}_cluster_{cid}_box_{i}.png"
                crop_path = os.path.join(crop_dir, crop_name)
                crop.save(crop_path)

                crop_paths.append("data/output/crops/" + base + "/" + crop_name)

        except Exception as e:
            crop_paths.append(f"crop_error: {str(e)}")

        results.append({
            "image": img_path,
            "csv": csv_path,
            "json": json_path,
            "clustered_image": web_clustered_url,
            "crops": crop_paths,
            "timestamp": timestamp
        })

    return jsonify({"results": results})


@cluster_bp.route('/export', methods=['POST'])
def export_cluster():
    data = request.get_json() or {}
    image_path = data.get('image_path')
    k = int(data.get('k', 8))
    out = export_clusters(image_path, k)
    return jsonify({'ok': True, 'out': out})
