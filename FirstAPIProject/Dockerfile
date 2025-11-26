# Основа
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект в контейнер
COPY . .

# Открываем наш порт 8000, на котором работает fastapi
EXPOSE 8000

# Запускаем
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]