# MAIN ENTRY TO THE BACKEND
# This file is the main entry point to the backend. It is responsible for creating the Flask app and running it.

from config.config import *
from app.app import create_app
from dotenv import load_dotenv
import subprocess
import os

if __name__ == '__main__':

    # create the Flask app
    app = create_app(DevelopmentConfig)

    # load env variables from .env file (dev only)
    load_dotenv(override=True)

    # check if running in development mode
    run_dev = True if os.environ.get('RUN_DEV') == "True" else False

    # if running locally, run the app with Flask's built-in server
    if run_dev:
        app.run(
            host='0.0.0.0',
            port=os.environ.get("PORT"),
            use_reloader=False,
            debug=True,
            # ssl_context=('ssl/localhost.crt', 'ssl/localhost.key')
        )

    # if running on Cloud, run with Gunicorn
    else:

        create_app(ProductionConfig)

        subprocess.run([
            "gunicorn", "-w", "2", "-b",
            f"0.0.0.0:{(os.environ.get('PORT'))}",
            # "--certfile", "ssl/localhost.csr",
            # "--keyfile", "ssl/localhost.key",
            "app.app:app"
        ])