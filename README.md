# Quickstart

- Clone the repo onto your machine
  ```
  git clone ...
  ```

- Create a virtual environment for dependencies
  ```
  python -m venv venv
  ```
- Create the environment variables (fill in missing variables)
  ```
  cp .env.template .env
  ```
- Run the Flask application
  ```
  python run.py
  ```

# Tools for Development

- **_Back-end_** - Flask
  
- **_Front-end_** - Vue.js, HTML/CSS, Bootstrap
  
- **_Data_** - mySQL, PostGREs

- **_DevOps_** - Git, Docker, K8s?, GitHub Actions

- **_Project Management_** - Asana, GitHub



# Tools/Libs for General Requirements

- **_GUI_** - Vue.js, Bootstrap

- **_Operational Env_** - Gunicorn, Heroku (PostGREs)

- **_Security Access_** - Flask-Login (or JWT)

- **_Roles and Privileges_** - Flask-Login, Flask-Session
  
- **_Auto Timeout Logoff_** - Flask-Login, Flask-Session
  
- **_Single Entry of Information_** - Central DB config
  
- **_Validation of Inputs_** - Flask-WTF, Bootstrap
  
- **_Entry and Processing of Names_** - Flask-WTF, SQLAlchemy (`ilike`)
  
- **_Modular Design_** - FS Organization, Flask-Blueprints, microservices arch (comm over HTTP)
  
- **_Data Structure_** - SQLAlchemy
  
- **_Display Printing_** - `@media print` CSS block, `window.print()` JS func, Flask-WeasyPrint
  
- **_Reporting Requirements_** - Same above ^
  
- **_Online Help Function_** - JSON file -> Jinja2, Tooltips
  
- **_Screens/User Interface_** - HTML, Jinja
  
- **_Ability to Access Any Screen_** - Central menu nav
  
- **_Prototype Design / Process_** - Confluence?
  
- **_Control of Info Entry Sequence_** - Flask-WTF
  
- **_Error Message_** - Bootstrap, JS
  
- **_Processing Block Until Error Corrected_** - Flask-WTF
  
- **_Control Entry Modification_** - Flask-Session
  
- **_Modification Consistency Checks_** - Flask endpoint logic
  
- **_User Cancellation of Action Before Completion_** - Same above ^
  
- **_Restoration of Previous Data_** - Flask-WTF, Flask-Session
