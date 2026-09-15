.PHONY: help install install-dev clean test lint format run docker-build docker-up

help:
	@echo "الأوامر المتاحة:"
	@echo "  install       تثبيت المتطلبات"
	@echo "  install-dev   تثبيت متطلبات التطوير"
	@echo "  test          تشغيل الاختبارات"
	@echo "  lint          فحص الكود"
	@echo "  format        تنسيق الكود"
	@echo "  run           تشغيل التطبيق"
	@echo "  docker-build  بناء صورة Docker"
	@echo "  docker-up     تشغيل docker-compose"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pre-commit install

test:
	pytest tests/ -v

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/ .mypy_cache/ htmlcov/ .coverage

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t algerian-digital-id -f docker/Dockerfile .

docker-up:
	docker-compose -f docker/docker-compose.yml up -d