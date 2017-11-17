#!/usr/local/bin/python3

import asyncio
import logging

log = logging.getLogger(__name__)


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        try:
            await self._callback()
        except Exception as e:
            log.exception("Timer Callback")

    def cancel(self):
        self._task.cancel()
