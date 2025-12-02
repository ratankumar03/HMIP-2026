# 🔌 WebSocket Consumers for Real-time Location Tracking
# File Location: backend/apps/location/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import logging

logger = logging.getLogger(__name__)

class LocationTrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time location tracking
    """
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.room_group_name = f'location_{self.user.id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.id} connected to location tracking")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User {self.user.id} disconnected from location tracking")
    
    async def receive(self, text_data):
        """
        Receive location data from WebSocket
        Expected format: {"latitude": 40.7128, "longitude": -74.0060, "accuracy": 10.5}
        """
        try:
            data = json.loads(text_data)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            accuracy = data.get('accuracy')
            
            if latitude is None or longitude is None:
                await self.send(text_data=json.dumps({
                    'error': 'Missing latitude or longitude'
                }))
                return
            
            # Store location in database
            await self.store_location(
                user_id=self.user.id,
                latitude=latitude,
                longitude=longitude,
                accuracy=accuracy,
                metadata=data.get('metadata', {})
            )
            
            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_update',
                    'latitude': latitude,
                    'longitude': longitude,
                    'accuracy': accuracy,
                    'user_id': str(self.user.id)
                }
            )
            
            # Send confirmation
            await self.send(text_data=json.dumps({
                'status': 'success',
                'message': 'Location updated'
            }))
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error processing location: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process location'
            }))
    
    async def location_update(self, event):
        """Send location update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'accuracy': event.get('accuracy'),
            'user_id': event['user_id']
        }))
    
    @database_sync_to_async
    def store_location(self, user_id, latitude, longitude, accuracy, metadata):
        """Store location data in database"""
        from .models import LocationData
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        return LocationData.objects.create(
            user=user,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy
        )


class LocationUpdatesConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for receiving real-time location updates of other users
    (for tracking/monitoring purposes with proper permissions)
    """
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope['user']
        self.tracked_user_id = self.scope['url_route']['kwargs']['user_id']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # TODO: Check if user has permission to track this user
        # For now, we'll allow connection
        self.room_group_name = f'location_{self.tracked_user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.id} subscribed to location updates of user {self.tracked_user_id}")
        
        # Send latest location immediately
        latest_location = await self.get_latest_location(self.tracked_user_id)
        if latest_location:
            await self.send(text_data=json.dumps({
                'type': 'initial_location',
                'location': latest_location
            }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User {self.user.id} unsubscribed from location updates")
    
    async def location_update(self, event):
        """Receive location update from room group and send to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'accuracy': event.get('accuracy'),
            'user_id': event['user_id']
        }))
    
    @database_sync_to_async
    def get_latest_location(self, user_id):
        """Get the latest location for a user"""
        from .models import LocationData
        
        try:
            latest = LocationData.objects.filter(
                user_id=user_id
            ).order_by('-timestamp').first()
            
            if latest:
                return {
                    'latitude': latest.latitude,
                    'longitude': latest.longitude,
                    'accuracy': latest.accuracy,
                    'timestamp': latest.timestamp.isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting latest location: {e}")
            return None