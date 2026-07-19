# Security rules

## All endpoints authenticate

Every handler is registered through App.register, which wraps it in
session authentication middleware. Public endpoints are not supported.
