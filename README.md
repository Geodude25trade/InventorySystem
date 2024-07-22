# Inventory Tracker

Welcome to Inventory Tracker! If you have a cooler name, please let me know!

## Setup Instructions

1. Start by cloning this repository
   1. `git clone git@github.com:Geodude25trade/InventorySystem.git`
2. Ensure you have Python 3 installed and then install the virtualenv package
   1. `pip install virtualenv`
3. navigate into the project folder and create a virtual environment
   1. `virtualenv env`
      1. If get an error about no command named `virtualenv` make sure you have the `Scripts/` folder for your python installation on your path
4. Activate the virtual environment
   1. Windows: `env/Scripts/activate.bat`
   2. Linux/MacOSX: `source env/bin/activate`
5. Install the required packages using the `requirements.txt` file located in the root folder of the project
   1. `pip install -r requirements.txt`
6. Create the `credentials.py` file
   1. Create a file named `credentials.py` in the root folder of the project and put the following information into it
   2. ```python
      APP_SECRET = "" # Generate a 32 bit secret key using os.urandom(32) and paste it here
      DATABASE_URI = 'sqlite:///[/Path/to/project/folder/database.db]'
      ```
7. Initialize the database (refer to [Import JSON](#importing-and-exporting-json) for how to load backed up data into the database)
   1. `flask initdb`
8. Start the web app
   1. Windows: `bin/start_local_dev.bat`
   2. Linux/MacOSX: `./bin/start_local_dev`
9. Navigate to [127.0.0.1:5000](http://127.0.0.1:5000) to view the web app

## Importing and Exporting JSON

You can export the data from an instance of the database to a `.json` file and import that data back into the database.

Export the database to `database.json` with
```commandline
flask export-json
```
and import a json file to fill the database with
```commandline
flask import-json path/to/database.json
```

## Project Dependencies
```text
click==8.0.3
colorama==0.4.4
Flask==2.0.2
Flask-SQLAlchemy==2.5.1
greenlet==1.1.2
itsdangerous==2.0.1
Jinja2==3.0.3
libsass==0.21.0
MarkupSafe==2.0.1
six==1.16.0
SQLAlchemy==1.4.28
Werkzeug==2.0.2
```