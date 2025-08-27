from flask_socketio import emit
import uuid

class RoomManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self, user1, user2):
        room_id = str(uuid.uuid4())
        self.rooms[room_id] = {
            "user1": user1,
            "user2": user2,
            "user1_socket": user1["socket_id"],
            "user2_socket": user2["socket_id"]
        }
        
        # Assign roles to avoid glare: user1 offers, user2 waits
        emit("send-offer", {"roomId": room_id}, room=user1["socket_id"])
        emit("wait-offer", {"roomId": room_id}, room=user2["socket_id"])

    def on_offer(self, room_id, sdp, sender_socket_id):
        room = self.rooms.get(room_id)
        if not room:
            return
        
        # Determine which user should receive the offer
        if sender_socket_id == room["user1_socket"]:
            emit("offer", {"roomId": room_id, "sdp": sdp}, room=room["user2_socket"])
        else:
            emit("offer", {"roomId": room_id, "sdp": sdp}, room=room["user1_socket"])

    def on_answer(self, room_id, sdp, sender_socket_id):
        room = self.rooms.get(room_id)
        if not room:
            return
        
        # Determine which user should receive the answer
        if sender_socket_id == room["user1_socket"]:
            emit("answer", {"roomId": room_id, "sdp": sdp}, room=room["user2_socket"])
        else:
            emit("answer", {"roomId": room_id, "sdp": sdp}, room=room["user1_socket"])

    def on_ice_candidates(self, room_id, sender_socket_id, candidate, type):
        room = self.rooms.get(room_id)
        if not room:
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
            del self.rooms[room_id]
            print(f"Room {room_id} removed")
