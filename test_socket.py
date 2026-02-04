import socket
try:
    result = socket.getaddrinfo('172.18.0.3', 5432)
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
