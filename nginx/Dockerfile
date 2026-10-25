# Используем официальный образ Nginx
FROM nginx:latest

RUN mkdir -p /app/staticfiles

# Копируем файл конфигурации Nginx в контейнер
COPY /nginx/nginx.conf /etc/nginx/nginx.conf

# Открываем 80 порт для HTTP-трафика
EXPOSE 80