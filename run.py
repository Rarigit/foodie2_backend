from app import app
from dbcreds import production_mode

if (production_mode == True):
    print("Running server in production mode")
    import bjoern #type:ignore
    bjoern.run(app, "0.0.0.0", 5009)
else:
    from flask_cors import CORS
    CORS(app)
    print("Running in testing mode")
    app.run(debug=True)
