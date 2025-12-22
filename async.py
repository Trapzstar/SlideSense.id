import asyncio

class HybridVoiceRecognizer:
    async def listen_async(self):
        # Non-blocking voice recognition
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.listen)