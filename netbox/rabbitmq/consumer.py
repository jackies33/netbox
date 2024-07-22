

from fastapi import FastAPI, Request, HTTPException
import json
import pika


from my_env import rabbitmq_host,rabbit_target_exchange,netbox_webhook_host

app = FastAPI()



def send_to_rabbitmq(route_key: str, message: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.basic_publish(
        exchange=rabbit_target_exchange,
        routing_key=route_key,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ))
    connection.close()

@app.post('/netbox_main/rabbitmq_proxy/{route_key}')# create path for netbox webhook
async def webhook_handler(route_key: str, request: Request):
    data = await request.json()
    if not data:
        raise HTTPException(status_code=400, detail="No data provided")
    print(data)
    message = json.dumps(data)
    send_to_rabbitmq(route_key, message)
    return {"message": f"Message sent to RabbitMQ queue: {route_key}"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=netbox_webhook_host, port=5005)


