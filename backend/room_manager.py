from flask_socketio import emit
import uuid
import time

class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.room_creation_times = {}  # Track when rooms were created
        self.connection_timeout = 30  # 30 seconds to establish connection

    def create_room(self, user1, user2):
        room_id = str(uuid.uuid4())
        current_time = time.time()
        
        self.rooms[room_id] = {
            "user1": user1,
            "user2": user2,
            "user1_socket": user1["socket_id"],
            "user2_socket": user2["socket_id"],
            "created_at": current_time,
            "connection_established": False,
            "offer_sent": False,
            "answer_sent": False
        }
        
        self.room_creation_times[room_id] = current_time
        
        print(f"Room {room_id} created for users {user1['name']} and {user2['name']}")
        
        # Assign roles to avoid glare: user1 offers, user2 waits
        # Pass partner names to both users
        emit("send-offer", {
            "roomId": room_id, 
            "partnerName": user2["name"]
        }, room=user1["socket_id"])
        
        emit("wait-offer", {
            "roomId": room_id, 
            "partnerName": user1["name"]
        }, room=user2["socket_id"])

    def on_offer(self, room_id, sdp, sender_socket_id):
        room = self.rooms.get(room_id)
        if not room:
            print(f"Offer received for non-existent room: {room_id}")
            return
        
        # Mark that offer has been sent
        room["offer_sent"] = True
        
        # Determine which user should receive the offer
        if sender_socket_id == room["user1_socket"]:
            emit("offer", {"roomId": room_id, "sdp": sdp}, room=room["user2_socket"])
        else:
            emit("offer", {"roomId": room_id, "sdp": sdp}, room=room["user1_socket"])

    def on_answer(self, room_id, sdp, sender_socket_id):
        room = self.rooms.get(room_id)
        if not room:
            print(f"Answer received for non-existent room: {room_id}")
            return
        
        # Mark that answer has been sent
        room["answer_sent"] = True
        
        # Determine which user should receive the answer
        if sender_socket_id == room["user1_socket"]:
            emit("answer", {"roomId": room_id, "sdp": sdp}, room=room["user2_socket"])
        else:
            emit("answer", {"roomId": room_id, "sdp": sdp}, room=room["user1_socket"])

    def on_ice_candidates(self, room_id, sender_socket_id, candidate, type):
        room = self.rooms.get(room_id)
        if not room:
            print(f"ICE candidate received for non-existent room: {room_id}")
            return
        
        # Determine which user should receive the ICE candidate
        if sender_socket_id == room["user1_socket"]:
            emit("add-ice-candidate", {"candidate": candidate, "type": type}, room=room["user2_socket"])
        else:
            emit("add-ice-candidate", {"candidate": candidate, "type": type}, room=room["user1_socket"])

    def handle_user_disconnect(self, socket_id):
        """
        Handle when a user disconnects from a room.
        Returns the remaining user if any, and the room_id for cleanup.
        """
        room_id = None
        remaining_user = None
        
        # Find the room containing the disconnected user
        for rid, room in list(self.rooms.items()):
            if room["user1_socket"] == socket_id:
                room_id = rid
                remaining_user = room["user2"]
                break
            elif room["user2_socket"] == socket_id:
                room_id = rid
                remaining_user = room["user1"]
                break
        
        if room_id:
            # Notify the remaining user about the disconnection
            if remaining_user:
                emit("partner-disconnected", room=remaining_user["socket_id"])
            
            # Remove the room
            del self.rooms[room_id]
            if room_id in self.room_creation_times:
                del self.room_creation_times[room_id]
            print(f"Room {room_id} removed due to user {socket_id} disconnection")
        
        return remaining_user

    def get_room_by_user(self, socket_id):
        """
        Get room information for a specific user.
        """
        for room_id, room in self.rooms.items():
            if room["user1_socket"] == socket_id or room["user2_socket"] == socket_id:
                return room_id, room
        return None, None

    def remove_room(self, room_id):
        if room_id in self.rooms:
            room = self.rooms[room_id]
            print(f"Room {room_id} removed for users {room['user1']['name']} and {room['user2']['name']}")
            del self.rooms[room_id]
            if room_id in self.room_creation_times:
                del self.room_creation_times[room_id]

    def get_room_count(self):
        """Get the current number of active rooms"""
        return len(self.rooms)

    def cleanup_stale_rooms(self):
        """Remove rooms that have been created but not connected for too long"""
        current_time = time.time()
        stale_rooms = []
        
        for room_id, creation_time in self.room_creation_times.items():
            if current_time - creation_time > self.connection_timeout:
                room = self.rooms.get(room_id)
                if room and not room.get("connection_established", False):
                    stale_rooms.append(room_id)
        
        for room_id in stale_rooms:
            room = self.rooms.get(room_id)
            if room:
                print(f"Removing stale room {room_id} - connection timeout")
                # Notify both users about the timeout
                emit("connection-timeout", room=room["user1_socket"])
                emit("connection-timeout", room=room["user2_socket"])
                del self.rooms[room_id]
                del self.room_creation_times[room_id]

    def is_user_in_room(self, socket_id):
        """Check if a user is currently in any room"""
        return self.get_room_by_user(socket_id)[0] is not None

    def get_room_stats(self):
        """Get statistics about rooms"""
        total_rooms = len(self.rooms)
        connected_rooms = sum(1 for room in self.rooms.values() if room.get("connection_established", False))
        pending_rooms = total_rooms - connected_rooms
        
        return {
            "total_rooms": total_rooms,
            "connected_rooms": connected_rooms,
            "pending_rooms": pending_rooms,
            "connection_timeout": self.connection_timeout
        }
