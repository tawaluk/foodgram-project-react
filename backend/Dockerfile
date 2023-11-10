FROM python:3.11.6
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod +x test_run.sh
CMD ["./test_run.sh"]