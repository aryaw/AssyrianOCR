import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from flask import Flask, send_from_directory
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_mapping(SECRET_KEY=os.getenv("SECRET_KEY","dev"))

    from web.routes.upload_routes import upload_bp
    from web.routes.cluster_routes import cluster_bp
    # from web.routes.training_routes import training_bp
    from web.routes.model_routes import model_bp
    from web.routes.health_routes import health_bp

    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(cluster_bp, url_prefix="/api/cluster")
    # app.register_blueprint(training_bp, url_prefix="/api/train")
    app.register_blueprint(model_bp, url_prefix="/api/models")
    app.register_blueprint(health_bp, url_prefix="/api/health")

    from web.routes.ocr_routes import ocr_bp
    app.register_blueprint(ocr_bp, url_prefix="/api/ocr")

    from web.routes.restore_routes import restore_bp
    app.register_blueprint(restore_bp, url_prefix="/api/restore")

    @app.route('/')
    def index():
        print("LOADING INDEX.HTML") 
        return send_from_directory('templates','index.html')

    @app.route('/data/raw_images/', defaults={'filename': None})
    @app.route('/data/raw_images/<path:filename>')
    def raw_images(filename=None):
        if filename is None:
            return "No filename provided"
        else:
            return send_from_directory(os.path.join(os.getcwd(), 'data/raw_images'), filename)

    @app.route('/data/output/img_clustered/', defaults={'filename': None})
    @app.route('/data/output/img_clustered/<path:filename>')
    def output_clustered_images(filename=None):
        import os
        if filename is None:
            return "No filename provided"
        else:
            return send_from_directory(
                os.path.join(os.getcwd(), 'data/output/img_clustered'),
                filename
            )

    @app.route('/data/output/restored/', defaults={'filename': None})
    @app.route('/data/output/restored/<path:filename>')
    def restored_files(filename=None):
        if filename is None:
            return "No filename provided"
        else:
            return send_from_directory(os.path.join(os.getcwd(), 'data/output/restored'), filename)

    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8501))
    app.run(host='0.0.0.0', port=port, debug=True)
