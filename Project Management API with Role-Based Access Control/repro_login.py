from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, RoleEnum
from app.utils import get_password_hash

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

session = SessionLocal()
user = User(full_name='Admin Two', email='admin2@gmail.com', password=get_password_hash('admin'), role=RoleEnum.admin)
session.add(user)
session.commit()
session.close()

client = TestClient(app)
resp = client.post('/auth/login', data={'username': 'admin2@gmail.com', 'password': 'admin', 'role': 'Admin'})
print('status', resp.status_code)
print('headers', resp.headers)
print('text', resp.text)
try:
    print('json', resp.json())
except Exception as e:
    print('json error', e)
