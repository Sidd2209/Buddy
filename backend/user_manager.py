from flask_socketio import emit
from room_manager import RoomManager
import threading

class UserManager:
    def __init__(self):
        self.users = {}  # socket_id -> user_data
        self.queue = []
        self.room_manager = RoomManager()
        self.lock = threading.Lock()  # Thread safety for queue operations

    def add_user(self, name, socket_id):
        with self.lock:
            # Add user to users dict
            self.users[socket_id] = {"name": name, "socket_id": socket_id, "state": "queue"}
            
            # Add to queue
            if socket_id not in self.queue:
                self.queue.append(socket_id)
                print(f"User {socket_id} added to queue. Queue length: {len(self.queue)}")
            
            emit("lobby", room=socket_id)
            self.clear_queue()
        self.init_handlers(socket_id)

    def enqueue_user(self, socket_id):
        with self.lock:
            # Check if user exists and is not already in queue or room
            if socket_id not in self.users:
                print(f"User {socket_id} not found in users")
                return
                
            user = self.users[socket_id]
            current_state = user.get("state", "unknown")
            
            # Only enqueue if user is not already queued and not in a room
            if current_state == "queue" and socket_id in self.queue:
                print(f"User {socket_id} already in queue")
                return
                
            if current_state == "room":
                print(f"User {socket_id} is in a room, cannot enqueue")
                return
            
            # Update user state and add to queue
            user["state"] = "queue"
            if socket_id not in self.queue:
                self.queue.append(socket_id)
                print(f"User {socket_id} enqueued. Queue length: {len(self.queue)}")
                emit("lobby", room=socket_id)
                self.clear_queue()

    def next_user(self, socket_id):
        """
        Omegle-style next: only works if user is in a room.
        If in a room, tear it down, notify partner, and enqueue both.
        If not in a room (just waiting), ignore the request.
        """
        with self.lock:
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

                # Update user states
                if socket_id in self.users:
                    self.users[socket_id]["state"] = "queue"
                if partner_socket in self.users:
                    self.users[partner_socket]["state"] = "queue"

                # Remove room and notify both sides appropriately
                self.room_manager.remove_room(room_id)
                emit("partner-disconnected", room=partner_socket)

                # Enqueue both users
                self.enqueue_user(socket_id)
                self.enqueue_user(partner_socket)
            else:
                # User is not in a room (just waiting in queue) - ignore next request
                print(f"User {socket_id} requested next but is not in a room (just waiting)")
                # Don't do anything - let them continue waiting

    def remove_user(self, socket_id):
        with self.lock:
            # First, handle room disconnection
            remaining_user = self.room_manager.handle_user_disconnect(socket_id)
            
            # Remove user from users dict
            if socket_id in self.users:
                del self.users[socket_id]
            
            # Remove user from queue if they're in it
            if socket_id in self.queue:
                self.queue.remove(socket_id)
            
            # If there's a remaining user from a room, add them back to queue
            if remaining_user:
                remaining_socket_id = remaining_user["socket_id"]
                print(f"User {remaining_socket_id} returned to queue after partner disconnected")
                
                # Update remaining user's state
                if remaining_socket_id in self.users:
                    self.users[remaining_socket_id]["state"] = "queue"
                
                # Add to queue if not already there
                if remaining_socket_id not in self.queue:
                    self.queue.append(remaining_socket_id)
                    emit("lobby", room=remaining_socket_id)
                    self.clear_queue()
            
            print(f"User {socket_id} removed. Queue length: {len(self.queue)}")

    def clear_queue(self):
        print("Inside clearQueue")
        print("Queue length:", len(self.queue))

        if len(self.queue) < 2:
            return

        # Get two users from queue
        id1 = self.queue.pop(0)  # Use pop(0) to get FIFO behavior
        id2 = self.queue.pop(0)
        print(f"Pairing users: {id1} and {id2}")

        # Verify both users still exist and are in queue state
        if id1 not in self.users or id2 not in self.users:
            print("Pairing failed: One or both users not found in users dict.")
            # Put users back in queue if pairing failed
            if id1 in self.users:
                self.queue.insert(0, id1)
            if id2 in self.users:
                self.queue.insert(0, id2)
            return

        user1 = self.users[id1]
        user2 = self.users[id2]

        # Check if users are in correct state
        if user1.get("state") != "queue" or user2.get("state") != "queue":
            print("Pairing failed: Users not in queue state.")
            # Put users back in queue
            self.queue.insert(0, id1)
            self.queue.insert(0, id2)
            return

        # Update user states to room
        user1["state"] = "room"
        user2["state"] = "room"

        print("Creating room...")
        self.room_manager.create_room(user1, user2)
        
        # Continue processing queue
        self.clear_queue()

    def init_handlers(self, socket_id):
        # Handlers are now managed in the main app.py file
        pass

    def get_user_by_socket(self, socket_id):
        """
        Get user information by socket ID.
        """
        return self.users.get(socket_id)

    def is_user_in_queue(self, socket_id):
        """
        Check if a user is currently in the queue.
        """
        return socket_id in self.queue and socket_id in self.users and self.users[socket_id].get("state") == "queue"

    def is_user_in_room(self, socket_id):
        """
        Check if a user is currently in a room.
        """
        return socket_id in self.users and self.users[socket_id].get("state") == "room"

    def get_queue_status(self):
        """
        Get current queue status for debugging.
        """
        with self.lock:
            return {
                "queue_length": len(self.queue),
                "queue_users": self.queue.copy(),
                "total_users": len(self.users),
                "user_states": {socket_id: user.get("state", "unknown") for socket_id, user in self.users.items()}
            }
