# generic imports
import json
import sys
import logging
import pika

from requests import Request, Session

from django.conf import settings
from django.core.management.base import BaseCommand

from publisher.utils import get_backofftime
from publisher.amqp import RabbitMQBackend
from publisher.app_settings import STATUS
from publisher.helpers import update_events_details


logger = logging.getLogger(__name__)


def callback(ch, method, properties, body):
    """
    Callback method to consume messages from shared queue

    :params ch: channel name
    :params method: method name
    :params properties: channel level properties
    :params body: consumed message body
    """
    print "[X] Received message %s" % body
    s = Session()
    if ch.is_closed:
        backend = RabbitMQBackend()
        backend.open()
        channel = backend.channel
    else:
        channel = ch

    try:
        body = json.loads(body)
        max_retries = body["maxretries"]
        http_method = body["method"]
        text = body["message"]
        url = body["url"]
        headers = body.get("headers", dict())
        params = body.get("params", dict())
        callback_details = body['callback']
        update_events_details(
            body["request_id"], STATUS.SENT, callback_details,
            maxRetries=max_retries
        )

        req = Request(http_method, url, data=text, headers=headers)
        req = req.prepare()
        resp = s.send(
            req, timeout=settings.REQ_TIMEOUT, verify=False
        )
        resp.raise_for_status()
        update_events_details(
            body["request_id"], STATUS.DLV, callback_details,
            maxRetries=max_retries
        )
    except KeyError as e:
        update_events_details(
            body["request_id"], STATUS.FAIL,
            callback_details,
            maxRetries=max_retries
        )
        logger.error(
            "Important key %s missing,"
            " message can not be processed"
        )
    except Exception as e:
        update_events_details(
            body["request_id"],
            STATUS.FAIL, callback_details,
            maxRetries=max_retries
        )
        logger.exception(
            "Sorry! message can not be processed,"
            " MaxRetries exhausted"
        )
    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)


class Command(BaseCommand):
    """
    Worker management command
    """
    help = 'Command to start consumers'

    PREFETCH_COUNT = 100

    def handle(self, *args, **options):
        """
        Command handler
        """
        exchange = settings.PUBLISH_EXCHANGE
        queue = settings.PUBLISH_QUEUE
        backend = RabbitMQBackend()
        backend.open()
        try:
            backend.channel.basic_qos(prefetch_count=self.PREFETCH_COUNT)
            queue_name = backend.create_queue(
                queue, exclusive=False
            )
            backend.queue_bind(
                exchange=exchange,
                queue=queue,
                routing_key=queue
            )
            backend.basic_consume(callback, queue=queue, no_ack=False)
            logger.info("[X] Started worker pointing to %s-%s" % (
                exchange, queue)
            )
            backend.start_consuming()
        except Exception as e:
            logger.error(
                "Worker exited due to some critical error %s,"
                " please check !" % str(e)
            )
            raise e
        except KeyboardInterrupt as e:
            logger.info("[X] Got signal for quiting the program, quiting...")
            backend.close()
            sys.exit(0)
