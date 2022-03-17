# Официальный номер Node
FROM node

# Установка папки по умолчанию (в контейнере)
WORKDIR /app

# Добавление пути `/app/node_modules/.bin` в переменную среды $PATH
ENV PATH /app/node_modules/.bin:$PATH

# Установка зависимостей
COPY sample/package.json ./
COPY sample/package-lock.json ./
RUN npm install --silent
RUN npm install react-scripts@5.0.0 -g --silent

# Копирование проекта
COPY sample/ ./

# Запуск проекта
CMD ["npm", "start"]