import pika
import json
import logging
from threading import Thread
from datetime import datetime

logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self, rabbitmq_url: str = None):
        self.rabbitmq_url = rabbitmq_url or "amqp://admin:admin123@rabbitmq-node-1:5672/"
        self.connection = None
        self.channel = None
        
    def connect(self):
        try:
            credentials = pika.PlainCredentials('admin', 'admin123')
            parameters = pika.ConnectionParameters(
                host='rabbitmq-node-1',
                port=5672,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Γ£ô Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def declare_exchanges_and_queues(self):
        try:
            # Declare exchanges
            self.channel.exchange_declare('roadmap.events', exchange_type='topic', durable=True)
            self.channel.exchange_declare('blueprint.events', exchange_type='topic', durable=True)
            logger.info("Γ£ô Declared roadmap.events exchange")
            logger.info("Γ£ô Declared blueprint.events exchange")
            
            # Declare queues for roadmap service
            self.channel.queue_declare('roadmap_blueprint_events', durable=True)
            logger.info("Γ£ô Declared roadmap_blueprint_events queue")
            
            # Bind queues
            self.channel.queue_bind('roadmap_blueprint_events', 'blueprint.events', 'blueprint.created')
            self.channel.queue_bind('roadmap_blueprint_events', 'blueprint.events', 'blueprint.updated')
            logger.info("Γ£ô Bound blueprint.events to roadmap_blueprint_events")
            
        except Exception as e:
            logger.error(f"Error declaring exchanges/queues: {e}")
    
    def on_blueprint_event(self, ch, method, properties, body):
        try:
            event = json.loads(body)
            logger.info(f"Γ£ô Received blueprint event: {event.get('event_type')}")
            
            # Handle blueprint events
            event_type = event.get('event_type')
            if event_type == 'blueprint.created':
                logger.info(f"Blueprint created: {event['data'].get('blueprint_id')}")
            elif event_type == 'blueprint.updated':
                logger.info(f"Blueprint updated: {event['data'].get('blueprint_id')}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing blueprint event: {e}")
    
    def start_consuming(self):
        try:
            self.connect()
            self.declare_exchanges_and_queues()
            
            # Register consumer
            self.channel.basic_consume('roadmap_blueprint_events', self.on_blueprint_event)
            logger.info("Γ£ô Registered blueprint event consumer")
            
            logger.info("Γ£ô Starting event consumer... waiting for messages")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Consumer error: {e}")

def start_consumer_background():
    try:
        consumer = RabbitMQConsumer()
        thread = Thread(target=consumer.start_consuming, daemon=True)
        thread.start()
        logger.info("Γ£ô Event consumer started in background")
        return thread
    except Exception as e:
        logger.error(f"Failed to start consumer: {e}")
        return None
