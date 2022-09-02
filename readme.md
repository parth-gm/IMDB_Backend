## IMDB Backend

Tech Used: Python, FastAPI and SQLite

### Steps to Run

#### Locally Run via virtualenv

- `cd IMDB_BACKEND`
- Create Python Virtual Env 
```
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
```
- Install requirements.txt using `pip -r requirements.txt`
- Run server by `python main.py`

#### Using Dockerfile 

- `docker build -t youtube_app .`
- Update .env file (Based on your choice)
    - secret for JWT toen
    - algorithm = Token Algo
- `docker run  -p 8005:8005 -v {Absolute_Project_Path}/storage:/code/storage --env-file ./.env imdb_backend`

#### API doc
- Go to Swagger Doc at http://0.0.0.0:8005/docs#

