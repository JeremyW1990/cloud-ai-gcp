openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /v1/user/{user_id}:
    get:
      x-google-backend:
        address: ${api_services["users"]}
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
    put:
      x-google-backend:
        address: ${api_services["users"]}
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
    delete:
      x-google-backend:
        address: ${api_services["users"]}
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
  /v1/user:
    post:
      x-google-backend:
        address: ${api_services["users"]}
 