.env.example:
RETAILCRM_URL=https://your-store.retailcrm.ru
RETAILCRM_API_KEY=your_api_key_here

APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True


Local start:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload


Swagger ui: http://localhost:8000/docs


Docker:
docker-compose up -d --build
docker-compose down
docker-compose logs -f

