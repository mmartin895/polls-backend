#### Initialize python environment
`python3 -m venv env`

env activation:
- linux: `source env/bin/activate`
- windows: `env\Scripts\activate.bat`

#### Install required pip packages
Make sure you are positioned in root folder of project (folder where is manage.py and requirements.txt)

`pip install -r requirements.txt`

#### Migrate models to SQL database
`python manage.py makemigrations pollsapp`

`python manage.py migrate`

#### Create admin
`python manage.py createsuperuser`

- you will use provided credentials to sign in on `localhost:8000/admin`

#### Run backend server
`python manage.py runserver`
