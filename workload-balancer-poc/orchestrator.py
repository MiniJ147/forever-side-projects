"""
Orchestrator.py: focuses on collecting clients and then organizing hello 
"""
import socket
import asyncio

HOST = "127.0.0.1"
PORT = 3000
POLL_THROTTLE = 1

clients: list[socket.socket] = []

async def poll_clients():
    while True:
        # Make a copy of the list to avoid mutations during iteration
        for i, c in enumerate(list(clients)):
            try:
                data = c.recv(1024)
                if data:
                    print(f"Client {i}: {data.decode('utf-8')}")
            except BlockingIOError:
                # No data available right now, move to next client
                continue
            except ConnectionResetError:
                print("Client disconnected.")
                clients.remove(c)
                
        await asyncio.sleep(POLL_THROTTLE)

async def main():
    # 1. Fire and forget poll_clients in the background
    asyncio.create_task(poll_clients())

    # 2. Use asyncio's native non-blocking server socket loop
    loop = asyncio.get_running_loop()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        server_socket.setblocking(False) # Keep the server socket non-blocking
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            # 3. Securely await a new connection without freezing the thread
            conn, addr = await loop.sock_accept(server_socket)
            conn.setblocking(False)
            clients.append(conn)
            print(f"New client! Total clients: {len(clients)}")

asyncio.run(main())
