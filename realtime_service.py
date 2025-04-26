from fastapi import WebSocket
from typing import Dict, List
import json
from datetime import datetime
import math

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.driver_locations: Dict[str, dict] = {}
        self.ride_subscriptions: Dict[str, List[WebSocket]] = {}

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
            **location,
            'last_updated': datetime.utcnow().isoformat()
        }
        await self.broadcast_driver_updates()

    async def broadcast_driver_updates(self):
        for connection in self.active_connections.values():
            try:
                await connection.send_json({
                    'type': 'driverUpdate',
                    'drivers': list(self.driver_locations.values())
                })
            except:
                pass

    async def subscribe_to_ride_updates(self, ride_id: str, websocket: WebSocket):
        if ride_id not in self.ride_subscriptions:
            self.ride_subscriptions[ride_id] = []
        self.ride_subscriptions[ride_id].append(websocket)

    async def broadcast_ride_update(self, ride_id: str, data: dict):
        if ride_id in self.ride_subscriptions:
            for websocket in self.ride_subscriptions[ride_id]:
                try:
                    await websocket.send_json(data)
                except:
                    pass

    def _get_nearby_drivers(self, location: dict, radius_km: float = 5.0) -> List[dict]:
        nearby_drivers = []
        for driver_id, driver_location in self.driver_locations.items():
            distance = self._calculate_distance(
                location['lat'], location['lng'],
                driver_location['lat'], driver_location['lng']
            )
            if distance <= radius_km:
                nearby_drivers.append({
                    'id': driver_id,
                    'lat': driver_location['lat'],
                    'lng': driver_location['lng'],
                    'distance': distance
                })
        return nearby_drivers

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # Haversine formula to calculate distance between two points
        R = 6371  # Earth's radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

manager = ConnectionManager() 