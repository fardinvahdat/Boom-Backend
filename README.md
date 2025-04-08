├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   ├── versions/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   │   └── RRDB_ESRGAN_x4.pth
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── security.py
│   │   └──  image_processing.py
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── api_v1.py
│           └── endpoints/
│               ├── __init__.py
│               └── auth.py
│               └── images.py
│               └── init.py
│               └── users.py
├── requirements.txt
├── alembic.ini
└── .env