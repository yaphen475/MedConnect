import json
import time

from django.db import close_old_connections
from django.http import StreamingHttpResponse


POLL_INTERVAL_SECONDS = 1
HEARTBEAT_INTERVAL_SECONDS = 15


def encode_event(data, event, event_id):
    lines = [f"id: {event_id}", f"event: {event}"]
    lines.append(f"data: {json.dumps(data, ensure_ascii=False)}")
    return "\n".join(lines) + "\n\n"


def event_stream(poll_events):
    yield ": connected\n\n"
    last_heartbeat = time.monotonic()
    try:
        while True:
            close_old_connections()
            events = poll_events()
            for data, event, event_id in events:
                yield encode_event(data, event, event_id)
                last_heartbeat = time.monotonic()

            if time.monotonic() - last_heartbeat >= HEARTBEAT_INTERVAL_SECONDS:
                yield ": keep-alive\n\n"
                last_heartbeat = time.monotonic()

            time.sleep(POLL_INTERVAL_SECONDS)
    finally:
        close_old_connections()


def streaming_response(poll_events):
    response = StreamingHttpResponse(
        event_stream(poll_events),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache, no-transform"
    response["X-Accel-Buffering"] = "no"
    return response
