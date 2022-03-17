# Образ python
FROM python:3.9

# Текущий каталог, в котором будет находится код проекта
WORKDIR /code

# Сначала копируем файл с зависимостями
COPY ./requirements.txt /code/requirements.txt

# Устанавливаем все зависимости
# Опция --no-cache-dir указывает pip не сохранять загруженные пакеты локально,
# так как это возможно только в том случае, если pip будет запущен снова для установки тех же пакетов,
# но это не так при работе с контейнерами.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Копируем весь остальной код
COPY ./app /code/app

# Запускаем наше приложение
CMD ["uvicorn", "app.basket:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]