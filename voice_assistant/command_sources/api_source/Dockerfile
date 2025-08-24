FROM python:3.12-slim
WORKDIR /app
RUN pip install fastapi uvicorn
COPY source.py source.py
CMD ["uvicorn", "source:app", "--host", "0.0.0.0", "--port", "8000"]
