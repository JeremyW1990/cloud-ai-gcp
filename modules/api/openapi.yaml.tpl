swagger: "2.0"
info:
  title: Cloud-AI-API
  version: 1.0.0
paths:
  /v1/user/{user_id}:
    get:
      operationId: "getUserById"
      x-google-backend:
        address: address: ${api_services["user"]}
      parameters:
        - name: user_id
          in: path
          required: true
          type: string
      responses:
        200:
          description: "Successful response"
    put:
      operationId: "updateUserById"
      x-google-backend:
        address: address: ${api_services["user"]}
      parameters:
        - name: user_id
          in: path
          required: true
          type: string
      responses:
        200:
          description: "Successful response"
    delete:
      operationId: "deleteUserById"
      x-google-backend:
        address: address: ${api_services["user"]}
      parameters:
        - name: user_id
          in: path
          required: true
          type: string
      responses:
        200:
          description: "Successful response"
  /v1/user:
    post:
      operationId: "createUser"
      x-google-backend:
        address: address: ${api_services["user"]}
      responses:
        200:
          description: "Successful response"

        
 