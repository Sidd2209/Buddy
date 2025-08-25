from flask_socketio import emit
from room_manager import RoomManager

class UserManager:
    def __init__(self):
        self.users = []
        self.queue = []
        self.room_manager = RoomManager()

    def add_user(self, name, socket_id):
        self.users.append({"name": name, "socket_id": socket_id})
        self.queue.append(socket_id)
        emit("lobby", room=socket_id)
        self.clear_queue()
        self.init_handlers(socket_id)

    def remove_user(self, socket_id):
        self.users = [user for user in self.users if user["socket_id"] != socket_id]
        self.queue = [id for id in self.queue if id != socket_id]

    def clear_queue(self):
        print("Inside clearQueue")
        print("Queue length:", len(self.queue))

        if len(self.queue) < 2:
            return

        id1 = self.queue.pop()
        id2 = self.queue.pop()
        print(f"Pairing users: {id1} and {id2}")

        user1 = next((user for user in self.users if user["socket_id"] == id1), None)
        user2 = next((user for user in self.users if user["socket_id"] == id2), None)

        if not user1 or not user2:
            print("Pairing failed: One or both users not found.")
            return

        print("Creating room...")
        self.room_manager.create_room(user1, user2)
        self.clear_queue()

    def init_handlers(self, socket_id):
        # Handlers are now managed in the main app.py file
        pass
