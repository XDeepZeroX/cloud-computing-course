from fastapi import FastAPI

prefix = '/api/messages'
openapi_url = f'{prefix}/openapi.json'

app = FastAPI(openapi_url=openapi_url)

@app.get(f"{prefix}/ping")
async def ping():
    return "pong"


@app.get(prefix)
async def messages():
    return [
        {
            'id': 1,
            'message': 'Сообщение 1'
        },
        {
            'id': 2,
            'message': 'Сообщение 2'
        },
        {
            'id': 3,
            'message': 'Сообщение 3'
        },
    ]
