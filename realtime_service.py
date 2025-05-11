from fastapi import WebSocket
from typing import Dict, List, Optional, Set
import json
from datetime import datetime
import math
import asyncio
from sqlalchemy.orm import Session

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.driver_locations: Dict[str, dict] = {}
        self.ride_subscriptions: Dict[str, List[WebSocket]] = {}
        self.rider_requests: Dict[str, dict] = {}  # Rider requests with location info
        self.driver_subscriptions: Set[str] = set()  # Drivers looking for rides

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected. Total active connections: {len(self.active_connections)}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected. Total active connections: {len(self.active_connections)}")
        
        if user_id in self.driver_locations:
            del self.driver_locations[user_id]
            print(f"Driver {user_id} location tracking stopped")
        
        if user_id in self.driver_subscriptions:
            self.driver_subscriptions.remove(user_id)
            print(f"Driver {user_id} unsubscribed from ride requests")
            
        if user_id in self.rider_requests:
            del self.rider_requests[user_id]
            print(f"Rider {user_id} request removed")
            
        # Remove from ride subscriptions if present
        for ride_id, websockets in list(self.ride_subscriptions.items()):
            if user_id in [ws.client_state.get("user_id") for ws in websockets if hasattr(ws, "client_state")]:
                self.ride_subscriptions[ride_id] = [
                    ws for ws in websockets 
                    if not hasattr(ws, "client_state") or ws.client_state.get("user_id") != user_id
                ]
                if not self.ride_subscriptions[ride_id]:
                    del self.ride_subscriptions[ride_id]
                print(f"User {user_id} unsubscribed from ride {ride_id}")

    async def update_driver_location(self, driver_id: str, location: dict):
        """Update driver's location and notify relevant riders"""
        prev_location = self.driver_locations.get(driver_id)
        
        self.driver_locations[driver_id] = {
            "driver_id": driver_id,
            "lat": location['lat'],
            "lng": location['lng'],
            "heading": location.get('heading', 0),
            "speed": location.get('speed', 0),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # If driver is assigned to a ride, notify the rider
        for ride_id, websockets in self.ride_subscriptions.items():
            if ride_id.startswith(f"ride_{driver_id}_"):
                await self._notify_ride_participants(ride_id, {
                    'type': 'driver_location_update',
                    'location': self.driver_locations[driver_id]
                })
        
        # If significant movement (more than 100m), check for new ride matches
        if prev_location and self._calculate_distance(
            prev_location['lat'], prev_location['lng'],
            location['lat'], location['lng']
        ) > 0.1 and driver_id in self.driver_subscriptions:
            await self._check_for_ride_matches(driver_id)

        # Broadcast to all clients interested in driver locations
        await self.broadcast_driver_updates()

    async def _check_for_ride_matches(self, driver_id: str):
        """Check if driver matches any pending ride requests"""
        driver_location = self.driver_locations.get(driver_id)
        if not driver_location:
            return
            
        for rider_id, request in self.rider_requests.items():
            # Skip if request is older than 5 minutes
            request_time = datetime.fromisoformat(request['timestamp'])
            if (datetime.utcnow() - request_time).total_seconds() > 300:
                continue
                
            # Calculate distance to pickup
            distance = self._calculate_distance(
                driver_location['lat'], driver_location['lng'],
                request['pickup_lat'], request['pickup_lng']
            )
            
            # If driver is within 3km, notify them of the ride request
            if distance <= 3.0:
                if driver_id in self.active_connections:
                    try:
                        await self.active_connections[driver_id].send_json({
                            'type': 'ride_request',
                            'request_id': request['request_id'],
                            'rider_id': rider_id,
                            'pickup': {
                                'lat': request['pickup_lat'],
                                'lng': request['pickup_lng'],
                                'address': request['pickup_address']
                            },
                            'dropoff': {
                                'lat': request['dropoff_lat'],
                                'lng': request['dropoff_lng'],
                                'address': request['dropoff_address']
                            },
                            'distance_to_pickup': round(distance, 2),
                            'estimated_fare': request['estimated_fare']
                        })
                    except Exception as e:
                        print(f"Error sending ride request to driver {driver_id}: {str(e)}")

    async def add_ride_request(self, rider_id: str, request_data: dict):
        """Add a new ride request from a rider"""
        request_id = f"request_{rider_id}_{datetime.utcnow().timestamp()}"
        self.rider_requests[rider_id] = {
            'request_id': request_id,
            'rider_id': rider_id,
            'pickup_lat': request_data['pickup_lat'],
            'pickup_lng': request_data['pickup_lng'],
            'pickup_address': request_data.get('pickup_address', ''),
            'dropoff_lat': request_data['dropoff_lat'],
            'dropoff_lng': request_data['dropoff_lng'],
            'dropoff_address': request_data.get('dropoff_address', ''),
            'estimated_fare': request_data.get('estimated_fare', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Find nearby drivers
        nearby_drivers = self._get_nearby_drivers(
            {
                'lat': request_data['pickup_lat'], 
                'lng': request_data['pickup_lng']
            },
            radius_km=5.0
        )
        
        # Notify nearby drivers
        for driver in nearby_drivers:
            driver_id = driver['id']
            if driver_id in self.active_connections and driver_id in self.driver_subscriptions:
                try:
                    await self.active_connections[driver_id].send_json({
                        'type': 'ride_request',
                        'request_id': request_id,
                        'rider_id': rider_id,
                        'pickup': {
                            'lat': request_data['pickup_lat'],
                            'lng': request_data['pickup_lng'],
                            'address': request_data.get('pickup_address', '')
                        },
                        'dropoff': {
                            'lat': request_data['dropoff_lat'],
                            'lng': request_data['dropoff_lng'],
                            'address': request_data.get('dropoff_address', '')
                        },
                        'distance_to_pickup': round(driver['distance'], 2),
                        'estimated_fare': request_data.get('estimated_fare', 0)
                    })
                except Exception as e:
                    print(f"Error sending ride request to driver {driver_id}: {str(e)}")
        
        return {
            'request_id': request_id,
            'nearby_drivers': len(nearby_drivers)
        }

    async def subscribe_to_rides(self, driver_id: str):
        """Subscribe driver to receive ride requests"""
        self.driver_subscriptions.add(driver_id)
        print(f"Driver {driver_id} subscribed to ride requests")
        
        # Immediately check for existing ride requests
        if driver_id in self.driver_locations:
            await self._check_for_ride_matches(driver_id)

    async def cancel_ride_request(self, rider_id: str):
        """Cancel a ride request"""
        if rider_id in self.rider_requests:
            del self.rider_requests[rider_id]
            print(f"Rider {rider_id} cancelled request")
            
            # Notify all drivers that the request is cancelled
            for driver_id in self.driver_subscriptions:
                if driver_id in self.active_connections:
                    try:
                        await self.active_connections[driver_id].send_json({
                            'type': 'ride_request_cancelled',
                            'rider_id': rider_id
                        })
                    except Exception as e:
                        print(f"Error sending cancellation to driver {driver_id}: {str(e)}")
            
            return True
        return False

    async def broadcast_driver_updates(self):
        """Broadcast driver location updates to all connected clients"""
        for connection in self.active_connections.values():
            try:
                await connection.send_json({
                    'type': 'driver_locations_update',
                    'drivers': list(self.driver_locations.values())
                })
            except Exception as e:
                print(f"Error broadcasting driver updates: {str(e)}")

    async def subscribe_to_ride_updates(self, ride_id: str, websocket: WebSocket):
        """Subscribe to updates for a specific ride"""
        if ride_id not in self.ride_subscriptions:
            self.ride_subscriptions[ride_id] = []
        self.ride_subscriptions[ride_id].append(websocket)
        print(f"Client subscribed to ride {ride_id}")

    async def broadcast_ride_update(self, ride_id: str, data: dict):
        """Broadcast an update about a specific ride"""
        await self._notify_ride_participants(ride_id, data)

    async def _notify_ride_participants(self, ride_id: str, data: dict):
        """Send notification to all participants of a ride"""
        if ride_id in self.ride_subscriptions:
            for websocket in self.ride_subscriptions[ride_id]:
                try:
                    await websocket.send_json(data)
                except Exception as e:
                    print(f"Error sending ride update: {str(e)}")

    def _get_nearby_drivers(self, location: dict, radius_km: float = 5.0) -> List[dict]:
        """Get drivers near a specific location"""
        nearby_drivers = []
        for driver_id, driver_location in self.driver_locations.items():
            # Skip if last update is older than 5 minutes
            try:
                last_updated = datetime.fromisoformat(driver_location['last_updated'])
                if (datetime.utcnow() - last_updated).total_seconds() > 300:
                    continue
            except (ValueError, KeyError):
                continue
                
            distance = self._calculate_distance(
                location['lat'], location['lng'],
                driver_location['lat'], driver_location['lng']
            )
            if distance <= radius_km:
                nearby_drivers.append({
                    'id': driver_id,
                    'lat': driver_location['lat'],
                    'lng': driver_location['lng'],
                    'distance': distance,
                    'last_updated': driver_location['last_updated']
                })
        # Sort by distance
        nearby_drivers.sort(key=lambda d: d['distance'])
        return nearby_drivers

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat/2) * math.sin(dlat/2) + 
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
            math.sin(dlon/2) * math.sin(dlon/2)
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

# Initialize connection manager singleton
manager = ConnectionManager() 