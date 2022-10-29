FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD uvicorn main:app --reload --port 8000; streamlit run home.py --server.port 8501