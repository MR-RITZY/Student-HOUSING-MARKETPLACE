FROM python:3.12-slim


WORKDIR /app


RUN pip install --no-cache-dir uv


COPY requirements.txt .


RUN uv pip install --system --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8080


CMD ["uvicorn", "src.stu_house_market.main:app", "--host", "0.0.0.0", "port", "8080"]

