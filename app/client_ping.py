#!/usr/bin/env python3
import asyncio
import random
import datetime

class Client:
    def __init__(self, client_id, host='192.168.85.10', port=5699):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.request_counter = 0
        self.log_file = f"client_{client_id}_log.txt"

    async def send_requests(self, writer):
        while True:
            try:
                await asyncio.sleep(random.uniform(0.3, 3.0))

                message = f"[{self.request_counter}] PING"
                request_time = datetime.datetime.now()
                log_line = f"{request_time.strftime('%Y-%m-%d')};{request_time.strftime('%H:%M:%S.%f')[:-3]};{message};"

                writer.write(f"{message}\n".encode())
                await writer.drain()

                self.log(log_line)
                self.request_counter += 1

            except asyncio.CancelledError:
                break

    async def receive_and_process(self, reader):
        while True:
            try:
                data = await reader.readline()
                if not data:
                    break

                response_message = data.decode().strip()
                response_time = datetime.datetime.now()

                if "keepalive" in response_message:
                    log_line = f"{response_time.strftime('%Y-%m-%d')};{response_time.strftime('%H:%M:%S.%f')[:-3]};;;{response_message}\n"
                else:
                    log_line = f"{response_time.strftime('%Y-%m-%d')};{response_time.strftime('%H:%M:%S.%f')[:-3]};RESPONSE;{response_message}\n"

                self.log(log_line)

            except asyncio.CancelledError:
                break

    def log(self, message):
        with open(self.log_file, 'a') as f:
            f.write(message)

    async def connect_to_server(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        print(f"Client {self.client_id} connected to the server.")

        request_task = asyncio.create_task(self.send_requests(writer))
        receive_task = asyncio.create_task(self.receive_and_process(reader))

        await asyncio.gather(request_task, receive_task)

        writer.close()
        await writer.wait_closed()

if __name__ == '__main__':
    client_id = 1  # Измените для каждого клиента
    client = Client(client_id)
    asyncio.run(client.connect_to_server())