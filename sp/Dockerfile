# Базовый образ
FROM python:3.9-slim-buster

# Обновление пакетов системы и установка зависимостей
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends git gcc g++ make && \
    rm -rf /var/lib/apt/lists/*

# Копирование всех файлов из текущей директории в рабочую директорию образа
COPY . /app
WORKDIR /app

# Установка PyTorch, Transformers и необходимых библиотек
RUN pip install torch==2.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html && \
    pip install transformers && \
    pip install flask flask-cors pydub librosa

# Запуск сервера
EXPOSE 5000
CMD [ "python", "./api.py" ]
