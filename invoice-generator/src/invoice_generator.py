import sys
import random
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING, Producer

def generate_invoice(producer):
    producer_topic = "invoice-generated"
    invoice_number = random.randint(1000, 99999)
    message = "Invoice number: #" + str(invoice_number) + " generated."
    producer.produce(producer_topic, message)
    producer.poll()
    producer.flush()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("config_file", type=FileType("r"))
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser["default"])

    producer = Producer(config)
    config.update(config_parser["consumer"])

    consumer = Consumer(config)

    def reset_offset(consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            consumer.assign(partitions)

    # Subscribe to topic
    topic = "generate-invoice"
    consumer.subscribe([topic], on_assign=reset_offset)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                pass

            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                print("Consumed event from topic {topic}: value = {value:12}".format(
                    topic=msg.topic(), value=msg.value().decode("utf-8")))

                generate_invoice(producer)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
