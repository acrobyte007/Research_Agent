import asyncio
import websockets

async def chat():
    uri = "ws://127.0.0.1:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("Enter your query (or 'exit' to quit):")
            while True:
                query = input("> ")
                if query.lower() == "exit":
                    break
                await websocket.send(query)
                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        print(response, end="")
                    except asyncio.TimeoutError:
                        break
                    except websockets.ConnectionClosed:
                        print("\nConnection closed by server.")
                        break
                print()
    except Exception as e:
        print(f"WebSocket Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")