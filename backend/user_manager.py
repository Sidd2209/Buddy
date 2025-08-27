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

    def enqueue_user(self, socket_id):
        # Only enqueue if user exists and is not already queued
        user = next((u for u in self.users if u["socket_id"] == socket_id), None)
        if not user:
            return
        if socket_id not in self.queue:
            self.queue.append(socket_id)
            emit("lobby", room=socket_id)
            self.clear_queue()

    def next_user(self, socket_id):
        """
        Omegle-style next: only works if user is in a room.
        If in a room, tear it down, notify partner, and enqueue both.
        If not in a room (just waiting), ignore the request.
        """
        # Find the room
        room_id, room = self.room_manager.get_room_by_user(socket_id)
        if room:
            # User is in a room - proceed with next
            print(f"User {socket_id} requested next from room {room_id}")
            
            # Identify partner
            if room["user1_socket"] == socket_id:
                partner_socket = room["user2_socket"]
            else:
                partner_socket = room["user1_socket"]

            # Remove room and notify both sides appropriately
            self.room_manager.remove_room(room_id)
            emit("partner-disconnected", room=partner_socket)

            # Enqueue both
            self.enqueue_user(socket_id)
            self.enqueue_user(partner_socket)
        else:
            # User is not in a room (just waiting in queue) - ignore next request
            print(f"User {socket_id} requested next but is not in a room (just waiting)")
            # Don't do anything - let them continue waiting

    def remove_user(self, socket_id):
        # First, handle room disconnection
        remaining_user = self.room_manager.handle_user_disconnect(socket_id)
        
        # Remove user from users list
        self.users = [user for user in self.users if user["socket_id"] != socket_id]
        
        # Remove user from queue if they're in it
        self.queue = [id for id in self.queue if id != socket_id]
        
        # If there's a remaining user from a room, add them back to queue
        if remaining_user:
            print(f"User {remaining_user['socket_id']} returned to queue after partner disconnected")
            # Check if user is not already in queue
            if remaining_user["socket_id"] not in self.queue:
                self.queue.append(remaining_user["socket_id"])
                emit("lobby", room=remaining_user["socket_id"])
                self.clear_queue()
        
        print(f"User {socket_id} removed. Queue length: {len(self.queue)}")

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
            # Put users back in queue if pairing failed
            if user1:
                self.queue.append(id1)
            if user2:
                self.queue.append(id2)
            return

        print("Creating room...")
        self.room_manager.create_room(user1, user2)
        self.clear_queue()

    def init_handlers(self, socket_id):
        # Handlers are now managed in the main app.py file
        pass

    def get_user_by_socket(self, socket_id):
        """
        Get user information by socket ID.
        """
        return next((user for user in self.users if user["socket_id"] == socket_id), None)

    def is_user_in_queue(self, socket_id):
        """
        Check if a user is currently in the queue.
        """
        return socket_id in self.queue

    def is_user_in_room(self, socket_id):
        """
        Check if a user is currently in a room.
        """
        room_id, _ = self.room_manager.get_room_by_user(socket_id)
        return room_id is not None
