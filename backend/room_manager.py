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
        
        # Send room creation event to both users
        emit("send-offer", {"roomId": room_id}, room=user1["socket_id"])
        emit("send-offer", {"roomId": room_id}, room=user2["socket_id"])

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
