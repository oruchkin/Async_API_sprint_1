## Running
To see logs only for the specific container use command
```
docker-compose up --attach tests --build
```



### запуск тестовых контейнеров redis/elastic/fastapi

```
docker-compose -p dev_tests -f docker-compose.dev.yml up --build
```

Запуск тестов коммандой:
```
pytest -s .
```


Локальный запуск тесов через makefile
```
make test
```
