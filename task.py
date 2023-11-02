from queue import Queue


class TaskQueue:

    def __init__(self):
        self.queue = Queue()

    def add(self, task):
        self.queue.put(task)

    def get(self):
        return self.queue.get()

    def empty(self):
        return self.queue.empty()

    def size(self):
        return self.queue.qsize()
    

"""

robot
- llm(commands) > action
- take image() > image
- move servos(action) > robotlog

"""


async def execute_task_batch(task_batch):
    results = []
    for task in task_batch:
        results.append(task())
    return results