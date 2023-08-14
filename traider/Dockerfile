# Используем базовый образ Ubuntu 20.04
FROM python:3.10

# Устанавливаем пакеты системы 
# RUN apt-get update && apt-get install -y \
#     python3.10 \
#     python3-pip \
#     && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы helper.py, chat.py, workFlask.py и workBinance.py в директорию /app контейнера
COPY workFlask.py traiderWork.py helper.py workYDB.py /app/

# Копируем файл requirements.txt в директорию /app контейнера
COPY requirements.txt /app/

# Устанавливаем зависимости из requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Открываем порт 5000 (или любой другой необходимый порт)
EXPOSE 5004

# Копируем файл .env внутрь контейнера
COPY .env authorized_key.json /app/

CMD ["python", "workFlask.py"]