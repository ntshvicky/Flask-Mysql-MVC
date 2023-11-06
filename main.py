
import os
from controllers.main_controller import app

from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    debugStatus = True if os.getenv('FLASK_RUN_DEBUG').lower() == "true" else False
    app.run(host='0.0.0.0', port=os.getenv('FLASK_RUN_PORT'), debug=debugStatus)
    