#!/usr/bin/env python3
import asyncio
import random
import datetime

class Server:
    def __init__(self, host='192.168.85.10', port=5699):
        self.host = host
        self.port = port
        self.clients = []
        self.request_counter = 0
        self.response_counter = 0
        self.log_file = "server_log.txt"

    async def handle_client(self, reader, writer):
        client_id = len(self.clients) + 1
        self.clients.append(writer)
        print(f"Client {client_id} connected.")
        
        while True:
            try:
                data = await reader.readline()
                
                if not data:
                    break

                message = data.decode().strip()
                request_time = datetime.datetime.now()
                log_line = f"{request_time.strftime('%Y-%m-%d')};{request_time.strftime('%H:%M:%S.%f')[:-3]};{message};"

                if random.random() < 0.1:
                    log_line += "(проигнорировано)\n"
                    self.log(log_line)
                    continue

                await asyncio.sleep(random.uniform(0.1, 1.0))

                response_message = f"[{self.response_counter}/{self.request_counter}] PONG ({client_id})"
                self.response_counter += 1

                writer.write(f"{response_message}\n".encode())
                await writer.drain()

                response_time = datetime.datetime.now()
                log_line += f"{response_time.strftime('%H:%M:%S.%f')[:-3]};{response_message}\n"
                self.log(log_line)

                self.request_counter += 1

            except asyncio.CancelledError:
                break

        print(f"Client {client_id} disconnected.")
        self.clients.remove(writer)
        writer.close()
        await writer.wait_closed()

    def log(self, message):
        with open(self.log_file, 'a') as f:
            f.write(message)

    async def send_keepalive(self):
        while True:
            await asyncio.sleep(5)
            if self.clients:
                response_message = f"[{self.response_counter}] keepalive"
                self.response_counter += 1

                for client in self.clients:
                    client.write(f"{response_message}\n".encode())
                    await client.drain()

    async def start_server(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"Server started on {self.host}:{self.port}")

        keepalive_task = asyncio.create_task(self.send_keepalive())

        async with server:
            await server.serve_forever()

        keepalive_task.cancel()

if __name__ == '__main__':
    server = Server()
    asyncio.run(server.start_server())