Shop AI 🛒 — A Scalable E-Commerce Platform Built with Django & PostgreSQL

Shop AI is a full-stack e-commerce application designed with production-grade architecture and clean, test-driven code.
Built using Django for robust backend logic.
The project demonstrates best practices in software engineering — modular app design, environment isolation, CI/CD, and >90 % pytest coverage.

🚀 Current Features

- **Users App** : Authentication, registration, and user profile management

- **Products App** : Product catalog and detail views

- **Cart App** : Cart logic with add/remove/update functionality

- **Orders App** : Order creation, management, and tracking

- **Checkout App** : Cart review, Stripe payment and receipt processing 

Test Suite: > 90 % coverage using pytest, integrated with GitHub Actions

Environment Management: Secure .env handling with django-environ

🛠️ Tech Stack

**Backend** : Django 5 , DJANGO REST FRAMEWORK

**Database** : PostgreSQL (configurable via .env)

**Testing** : Pytest, GitHub Actions CI

**Auth** : Django’s built-in system with extensible models
**Environment** : python-dotenv, django-environ

## Local Development

To run locally for development or demo purposes:
1. **Clone the repo**
```bash
git clone https://github.com/SylvioDev/shop_ai.git
cd shop_ai
```
3. **Install dependencies**
```bash
pip install requirements.txt
```
4. **Run migrations**
```bash
export DJANGO_SETTINGS_MODULE=shop_ai.settings.local
python manage.py migrate
```
6. **Start the development server**
```bash
python manage.py runserver --settings=shop_ai.settings.local 0.0.0.0:8000 
```
7. **Open your browser**
```bash
http://localhost:8000/products
```

🧩 Planned Enhancements

- RestAPI Service : API endpoints using DRF (Django Rest Framework)

- Chatbot Assistant (Optional): AI-powered shopping assistant using NLP models


🤝 Contributing 

Fork the repository

**1.** Create a new branch (git checkout -b feature/YourFeature)

**2.** Commit your changes (git commit -am 'Add feature')

**3.** Push to the branch (git push origin feature/YourFeature)

**4.** Open a pull request


