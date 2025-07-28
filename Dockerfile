FROM python:3.11-alpine as builder

WORKDIR /app

RUN apk add --no-cache libffi-dev gcc musl-dev \
 && pip install --no-cache-dir --target=/app/pdfminer pdfminer.six==20221105 \
 && rm -rf /root/.cache /var/cache/apk/*

# ---- Final tiny runtime ----
FROM python:3.11-alpine

WORKDIR /app

COPY --from=builder /app/pdfminer /usr/local/lib/python3.11/site-packages
COPY . .

CMD ["python", "process_pdfs.py"]

