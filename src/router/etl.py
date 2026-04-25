import csv
import io
import json
import os
import pika
from fastapi import APIRouter, UploadFile, File, HTTPException

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def get_rabbitmq_connection():

    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        return connection
    except Exception:
        raise

router = APIRouter(prefix="/etl", tags=["etl"])

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400)

    content = await file.read()
    text = content.decode('utf-8', errors='ignore')
    reader = csv.DictReader(io.StringIO(text))
    headers = set(reader.fieldnames or [])

    queue_name = None
    if "Food_Item" in headers and "Calories (kcal)" in headers:
        queue_name = "daily_food_queue"
    elif "Patient_ID" in headers and "Diet_Recommendation" in headers:
        queue_name = "diet_rec_queue"
    elif "Max_BPM" in headers and "Workout_Type" in headers:
        queue_name = "exercise_queue"
    else:
        raise HTTPException(status_code=400)

    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    for row in reader:
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(row),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    connection.close()
    return {"status": "success", "detected_queue": queue_name}