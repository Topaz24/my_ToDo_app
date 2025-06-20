FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_APP=to_do_list.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

