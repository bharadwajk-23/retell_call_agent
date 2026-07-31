# --- Build stage ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- Serve stage ---
FROM python:3.12-slim AS serve
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY serve.py ./
COPY --from=build /app/dist ./dist
EXPOSE 8005
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8005/')" || exit 1
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8005"]

