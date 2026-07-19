"""File upload handler."""

from config import limits


def handle_upload(request):
    body = request["stream"].read()
    limit = limits.max_upload_bytes()
    if len(body) > limit:
        return {"status": 413}
    request["store"].put(request["filename"], body)
    return {"status": 201}
