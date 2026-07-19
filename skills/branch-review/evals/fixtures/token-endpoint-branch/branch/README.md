# sessiond

A small session service.

## Endpoints

- `GET /health` - liveness probe (public)
- `GET /profile` - the calling user's profile
- `POST /tokens` - issue an API token for the calling user

API tokens expire after 24 hours.
