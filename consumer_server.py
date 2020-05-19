from kafka import KafkaConsumer
import json


class ConsumerServer(KafkaConsumer):
    def __init__(self, topic_name):
        self.topic_name = topic_name
        self.running = True

    def run(self):
        consumer = KafkaConsumer(
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            consumer_timeout_ms = 1000,
            client_id="0"
        )
        try:
            consumer.subscribe([self.topic_name])
            while self.running:
                for massage in consumer:
                    new_message = massage.decode('utf-8')
                    print(json.dumps(new_message, indent=2))
        finally:
            consumer.close()
    def shutdown():
        self.running = False

def main():
    consumer = ConsumerServer("com.police.service.calls")
    consumer.run()

if __name__ == "__main__":
    main()
