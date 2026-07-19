# Security rules

- All endpoints authenticate: every route is registered through
  Router.add_route, which wraps handlers with session authentication
  unless the route is explicitly registered with public=True.
- Never log credentials, session ids, or token values.
- Token and session lifetimes are expressed in seconds everywhere.
