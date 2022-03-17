from fastapi import FastAPI

prefix = '/api/basket'
openapi_url = f'{prefix}/openapi.json'

app = FastAPI(openapi_url=openapi_url)

@app.get(f"{prefix}/ping")
async def ping():
    return "pong"


@app.get(prefix)
async def basket():
    return {
        'Яблоки': {
            'Количество (кг)': 10,
            'Стоимость руб. (1 кг)': 110
        },
        'Конфеты': {
            'Количество (кг)': 1,
            'Стоимость руб. (1 кг)': 160
        },
        'Крупа': {
            'Количество (кг)': 4,
            'Стоимость руб. (1 кг)': 78.50
        },
        'Колбаса': {
            'Количество (кг)': 2,
            'Стоимость руб. (1 кг)': 470
        },
        'Консервы': {
            'Количество (кг)': 0.8,
            'Стоимость руб. (1 кг)': 70
        }
    }
