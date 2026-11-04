"""Consommateurs WebSockets - PROPRIETAIRE : Leonardo (US-17).

Stub minimal : accepte la connexion et renvoie un echo.
A completer : authentification (user connecte), controle d'appartenance au
thread, persistance dans messaging.Message, diffusion au cabinet + patient.
"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class MessagerieConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, content, **kwargs):
        await self.send_json({"type": "echo", "payload": content})
