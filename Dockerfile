FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
# If you have a requirements.txt, use:
# RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "generate.py"]
