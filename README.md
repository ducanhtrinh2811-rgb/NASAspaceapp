- create .env file like .env.example

- first time, u must fix the var ingestion/run=True in backend/config/config.yaml to load data
- next time u must replace it to false to ignore loading data

- run 2 command:
    - docker-compose build
    - docker-compose up


- note:
- docker-compose build for the first time may waste too much time (30p or 1h i dont know bout that.., it's up to your device), but next time it'll be faster

- docker-compose up to run backend


- if something failed, call me...