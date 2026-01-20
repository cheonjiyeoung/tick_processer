import threading
from typing import Optional
from dataclasses import dataclass
import time
import inspect

@dataclass
class Handler:
    func: callable
    thread: Optional[threading.Thread] = None

class TickProcesser:
    def __init__(self):
        self.handlers: dict[str, Handler] = {}
        self.data: Optional[dict] = None
        self.action_is_running = False


    def tick(self):
        if self.data is None:
            return
        topic = self.data.get('topic')
        value = self.data.get('value')
        handler = self.handlers.get(topic)
        if handler:
            if handler.thread and handler.thread.is_alive():
                print(f"Handler for topic '{topic}' is already running. Skipping new tick.")
                return
            elif handler.thread is not None and not handler.thread.is_alive():
                handler.thread = None
                print(f"Previous handler for topic '{topic}' has finished.")
                self.data = None
                self.action_is_running = False
                return
            elif handler.thread is None:
                # 함수가 파라미터를 받는지 확인
                sig = inspect.signature(handler.func)
                if len(sig.parameters) > 0:
                    thread = threading.Thread(target=handler.func, args=(value,), daemon=True)
                else:
                    thread = threading.Thread(target=handler.func, daemon=True)
                handler.thread = thread
                thread.start()
                self.action_is_running = True
        

    def register_handler(self, topic: str, func: callable):
        if topic not in self.handlers:
            self.handlers[topic] = Handler(func=func)

    def publish(self, data: dict):
        if not self.action_is_running:
            self.data = data

    def main_loop(self):
        while True:
            time.sleep(0.1)
            self.tick() 

if __name__ == "__main__":
    import random
    processer = TickProcesser()
    threading.Thread(target=processer.main_loop, daemon=True).start()

    def counter_5times():
        for i in range(5):
            print(f"Counter: {i+1}")
            time.sleep(1)
        print("Counter finished.")

    def counter_ABC():
        for char in ['A', 'B', 'C']:
            print(f"Counter: {char}")
            time.sleep(1)
        print("Counter finished.")

    def counter_with_value(value):
        print(f"Received value: {value}")
        for i in range(3):
            print(f"Processing {value} - step {i+1}")
            time.sleep(1)
        print(f"Finished processing {value}")

    processer.register_handler('count_5', counter_5times)
    processer.register_handler('count_ABC', counter_ABC)
    processer.register_handler('with_param', counter_with_value)

    lst_topics = [
        {'topic': 'count_5'},
        {'topic': 'count_ABC'},
        {'topic': 'with_param', 'value': 'Hello'},
        {'topic': 'with_param', 'value': 'World'},
    ]
    while True:
        data = random.choice(lst_topics)
        processer.publish(data)
        print(f"Published: {data}\n")
        time.sleep(random.uniform(5, 10))
