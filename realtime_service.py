from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.driver_locations: Dict[str, dict] = {}
        self.ride_updates: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.driver_locations:
            del self.driver_locations[user_id]

    async def update_driver_location(self, driver_id: str, location: dict):
        self.driver_locations[driver_id] = {
            "location": location,
            "timestamp": datetime.utcnow().isoformat()
        }
        # Notify all riders who are looking for nearby drivers
        await self.broadcast_nearby_drivers(location)

    async def broadcast_nearby_drivers(self, location: dict):
        nearby_drivers = self._get_nearby_drivers(location)
        message = {
            "type": "nearby_drivers",
            "data": nearby_drivers
        }
        # Broadcast to all connected riders
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except:
                self.disconnect(user_id)

    def _get_nearby_drivers(self, location: dict, radius_km: float = 5.0):
        nearby_drivers = []
        for driver_id, driver_data in self.driver_locations.items():
            if self._calculate_distance(location, driver_data["location"]) <= radius_km:
                nearby_drivers.append({
                    "driver_id": driver_id,
                    "location": driver_data["location"],
                    "last_update": driver_data["timestamp"]
                })
        return nearby_drivers

    def _calculate_distance(self, loc1: dict, loc2: dict) -> float:
        # Haversine formula to calculate distance between two points
        from math import radians, sin, cos, sqrt, atan2
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = radians(loc1["lat"]), radians(loc1["lng"])
        lat2, lon2 = radians(loc2["lat"]), radians(loc2["lng"])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    async def subscribe_to_ride_updates(self, ride_id: str, websocket: WebSocket):
        if ride_id not in self.ride_updates:
            self.ride_updates[ride_id] = []
        self.ride_updates[ride_id].append(websocket)

    async def broadcast_ride_update(self, ride_id: str, update: dict):
        if ride_id in self.ride_updates:
            for websocket in self.ride_updates[ride_id]:
                try:
                    await websocket.send_json(update)
                except:
                    self.ride_updates[ride_id].remove(websocket)

manager = ConnectionManager() 