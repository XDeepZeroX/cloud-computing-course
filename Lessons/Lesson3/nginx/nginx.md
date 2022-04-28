# Настройка конфигурации nginx <span id="nginx-python"></span>

Описание основных директив конфигурации nginx доступны по
ссылке: https://nginx.org/ru/docs/http/ngx_http_core_module.html

В проекте создадим директорию `nginx`, а в ней создадим файл `default.conf` и наполним его следующим содержимым:

```dockerfile
server {
  # Порт который будет принимать запросы
  listen 80;
  # IP адрес и порт который будет принимать запросы - любой IP и 80 порт
  listen [::]:80;
  # Задаёт имена виртуального сервера
  server_name _;
  # Разрешает или запрещает выдавать версию nginx’а на страницах ошибок и в поле “Server” заголовка ответа.
  server_tokens off;

  # Подгружаем блоки location из других файлов
  include /etc/nginx/conf.d/locations/*.locations;

  # Корзина
  # location - Устанавливает конфигурацию в зависимости от URI запроса.
  location /api/basket/ {
    # Задаёт протокол и адрес проксируемого сервера, а также необязательный URI, на который должен отображаться location
    proxy_pass http://python-basket-api;
  }
  # Корзина - документация (OpenAPI)
  location /api/basket/docs {
    proxy_pass http://python-basket-api/docs;
  }

  # Сообщения
  location /api/messages/ {
    proxy_pass http://python-messages-api;
  }
  # Сообщения - документация (OpenAPI)
  location /api/messages/docs {
    proxy_pass http://python-messages-api/docs;
  }
}
```

Конфигурация, без комментариев:

```dockerfile
server {
  listen 80;
  listen [::]:80;
  server_name _;
  server_tokens off;

  include /etc/nginx/conf.d/locations/*.locations;

  # Корзина
  location /api/basket/ {
    proxy_pass http://python-basket-api;
  }
  # Корзина - документация (OpenAPI)
  location /api/basket/docs {
    proxy_pass http://python-basket-api/docs;
  }

  # Сообщения
  location /api/messages/ {
    proxy_pass http://python-messages-api;
  }
  # Сообщения - документация (OpenAPI)
  location /api/messages/docs {
    proxy_pass http://python-messages-api/docs;
  }
}
```

# Настройка проекта

Если в системе есть UI модуль, для пользователей, он имеет встроенный nginx с конфигурацией всех микросервисов системы,
либо имеет тонкую конфигурацию для обработки общих запросов.

В случае с тонкой конфигурацией, настраивается проксирование (и др.) до внешнего nginx. Например, у нас есть 2 сервиса
backend и 1 frontend + 1 внешний nginx.

- Frontend содержит встроенный nginx и конфигурацию для проксирования URI, до внешнего nginx, которые начинаются
  с `/api/...`.
- Внешний nginx в свою очередь определяет к какому сервису идет запрос, и перенаправляет запрос к конкретному
  микросервису.

## Настройка docker-compose для внешнего nginx

```yaml
version: '3'

services:
  basket:
    <....config>
    networks:
      - python-api-tutorial
  messages:
    <....config>
    networks:
      - python-api-tutorial
  nginx:
    container_name: python-nginx-api
    hostname: python-nginx-api
    image: nginx
    restart: unless-stopped
    ports:
      - 6000:80
    # Прокидываем конфигурацию
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
    networks:
      - python-api-tutorial

# Контейнеры должны быть в одной сети, чтобы они могли обращаться друг к дургу по hostname, а не IP:PORT
networks:
  python-api-tutorial:
    external:
      name: python-api-tutorial
```


Теперь запрос:
```http
http://localhost:6000/api/basket
```

попадет в микросервис работы с корзиной. А запрос:

```http
http://localhost:6000/api/messages/ 
```

попадет в микросервис работы с сообщениями.


## Настройка встроенного nginx (React)

Конфигурация nginx выглядит следующим образом: 

```nginx
server {

  listen 80;

  location / {
    root /usr/share/nginx/html;
    index index.html index.htm;
    try_files $uri $uri/ /index.html;
  }

  error_page 500 502 503 504 /50x.html;

  location = /50x.html {
    root /usr/share/nginx/html;
  }

  location /api {
    proxy_pass http://niokrmain;
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    proxy_buffering off;
    proxy_set_header Accept-Encoding "";
  }

}
```


После этого необходимо изменить Dockerfile следующим образом: 

```dockerfile
# Официальный номер Node
FROM node as build
# Установка папки по умолчанию (в контейнере)
WORKDIR /app

# Добавление пути `/app/node_modules/.bin` в переменную среды $PATH
ENV PATH /app/node_modules/.bin:$PATH

# Установка зависимостей
COPY sample/ ./
RUN npm install

# Сборка проекта
RUN npm run build

# Production окружение 
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

# Запускаем nginx, который будет выдавать статичные данные frontend 
# и проксировать наши запросы до других сервисов
CMD ["nginx", "-g", "daemon off;"]
```


Конфигурация docker-compose не изменилась: 

```yml
version: '3'

services:

  react-sample-app:
    container_name: react-sample-app
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - 6001:80
    networks:
      - python-api-tutorial

networks:
  python-api-tutorial:
    external: 
      name: python-api-tutorial
```



# Другие примеры

## Настройка SSL сертификата

```dockerfile
server {
    listen 80;
    listen [::]:80;
    server_name name.domain.ru;
    server_tokens off;

    location / {
        return 301 https://$host$request_uri;
    }
}
server {
    listen 443 ssl;
    server_name name.domain.ru;

    ssl_certificate /etc/nginx/certs/name.domain.ru.cer;
    ssl_certificate_key /etc/nginx/certs/name.domain.ru.privatekey.key;


    keepalive_timeout 60;


    location /media/ {
        alias /home/media/;
    }
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://niokrmain;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        proxy_buffering off;
        proxy_set_header Accept-Encoding "";
    }

    error_page 500 502 503 504 /50x.html;

    location = /50x.html {
        root /usr/share/nginx/html;
    }
    client_max_body_size 100M;
}
```

где,

`name.domain.ru` - доменное имя вашего приложения

`client_max_body_size` - максимальный размер пересылаемых фалов

Указание путей к вашим SSL сертификатам (внутри контейнера)

```dockerfile
ssl_certificate /etc/nginx/certs/name.domain.ru.cer;
ssl_certificate_key /etc/nginx/certs/name.domain.ru.privatekey.key;
```

## Настройка поддержки WebSockets

```dockerfile
server {
    listen 80;
    listen [::]:80;
    server_name name.domain.ru;
    server_tokens off;

    location / {
        return 301 https://$host$request_uri;
    }
}
server {
    listen 443 ssl;
    server_name name.domain.ru;

    ssl_certificate /etc/nginx/certs/name.domain.ru.cer;
    ssl_certificate_key /etc/nginx/certs/name.domain.ru.privatekey.key;


    keepalive_timeout 60;


    location /media/ {
        alias /home/media/;
    }
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://niokrmain;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        proxy_buffering off;
        proxy_set_header Accept-Encoding "";
    }

    # WebSockets
    location /chathub {
        proxy_pass http://niokrmain;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    error_page 500 502 503 504 /50x.html;

    location = /50x.html {
        root /usr/share/nginx/html;
    }
    client_max_body_size 100M;
}
```
