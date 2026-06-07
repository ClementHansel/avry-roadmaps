import pika
import json
import logging
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Connection management
_connection = None
_channel = None

def get_connection():
    global _connection
    if _connection is None or _connection.is_closed:
        try:
            credentials = pika.PlainCredentials('admin', 'admin123')
            parameters = pika.ConnectionParameters(
                host='rabbitmq-node-1',
                port=5672,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            _connection = pika.BlockingConnection(parameters)
            logger.info("✓ Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"✗ RabbitMQ connection failed: {e}")
            raise
    return _connection

def get_channel():
    global _channel
    if _channel is None or _channel.is_closed:
        conn = get_connection()
        _channel = conn.channel()
    return _channel

def ensure_exchange(exchange_name: str, exchange_type: str = 'topic'):
    try:
        channel = get_channel()
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        logger.info(f"✓ Declared {exchange_name} exchange")
    except Exception as e:
        logger.error(f"✗ Failed to declare exchange: {e}")

def publish_event(
    exchange: str,
    routing_key: str,
    data: Dict[str, Any],
    event_type: str = None
) -> bool:
    try:
        channel = get_channel()
        
        event_data = {
            "event_type": event_type or routing_key,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(event_data),
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2
            )
        )
        
        logger.info(f"✓ Published {event_type} event")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to publish event: {e}")
        return False

def publish_roadmap_created(roadmap_id: str, user_id: str, **kwargs) -> bool:
    return publish_event(
        exchange='roadmap.events',
        routing_key='roadmap.created',
        data={"roadmap_id": roadmap_id, "user_id": user_id, **kwargs},
        event_type='roadmap.created'
    )

def publish_roadmap_updated(roadmap_id: str, user_id: str, **kwargs) -> bool:
    return publish_event(
        exchange='roadmap.events',
        routing_key='roadmap.updated',
        data={"roadmap_id": roadmap_id, "user_id": user_id, **kwargs},
        event_type='roadmap.updated'
    )

def publish_roadmap_shared(roadmap_id: str, shared_with: str, **kwargs) -> bool:
    return publish_event(
        exchange='roadmap.events',
        routing_key='roadmap.shared',
        data={"roadmap_id": roadmap_id, "shared_with": shared_with, **kwargs},
        event_type='roadmap.shared'
    )

def publish_milestone_completed(roadmap_id: str, milestone_id: str, **kwargs) -> bool:
    return publish_event(
        exchange='roadmap.events',
        routing_key='milestone.completed',
        data={"roadmap_id": roadmap_id, "milestone_id": milestone_id, **kwargs},
        event_type='milestone.completed'
    )
