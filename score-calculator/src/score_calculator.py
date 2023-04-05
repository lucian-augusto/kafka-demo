import sys
import random
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING, Producer

def calculate_score(producer):
    producer_topic = "score-calculated"
    invoice_number = random.randint(100,9999)
    message = "Calculated score: " + str(invoice_number) + ""
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

    # Create Consumer instance
    consumer = Consumer(config)

    # Set up a callback to handle the "--reset" flag.
    def reset_offset(consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            consumer.assign(partitions)

    # Subscribe to topic
    topic = "calculate-score"
    consumer.subscribe([topic], on_assign=reset_offset)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                # Extract the (optional) key and value, and print.

                print("Consumed event from topic {topic}: value = {value:12}".format(
                    topic=msg.topic(), value=msg.value().decode("utf-8")))

                calculate_score(producer)

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
