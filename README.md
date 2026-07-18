# FawatirAI Backend API

Welcome to the central Django REST Framework repository for the FawatirAI ERP project. 

## File Architecture & Team Domains

To keep our development clean and avoid merge conflicts, here is the breakdown of where your specific modules connect to this central hub. Please stick to your designated files!

### The Core Structure
```text
fawatir_backend/               
├── manage.py                  
├── fawatir_backend/           # Master Configuration Folder
│   ├── settings.py            
│   └── urls.py                
└── api/                       # Core API Application Folder
    ├── models.py              # Database Schema 
    ├── serializers.py         # JSON API Contracts 
    ├── views.py               # Backend logic (CRUD)
    └── urls.py                # API Endpoint routes


Team Assignments
@Fati (Database): The api/models.py file is your domain. This is where your PostgreSQL MCD is translated into Python code.

@Zineb (Frontend) & @Meryem (AI): You both will care about two files:

api/urls.py: This defines the exact endpoint links you will use to fetch or push data (e.g., http://127.0.0.1:8000/api/clients/).

api/serializers.py: This defines the exact JSON formats and contracts you will receive and need to send.

@Omar (DevOps/Integrations): The fawatir_backend/settings.py file is where you will eventually plug in the Docker configurations, production database credentials, and security settings.