swagger: "2.0"
info:
  title: Cloud-AI-API
  version: 1.0.0
paths:
  /v1/user/{user_id}:
    get:
      operationId: "getUserById"
      x-google-backend:
        address: "${user_service_url}"
        path_translation: APPEND_PATH_TO_ADDRESS
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
        address: "${user_service_url}"
        path_translation: APPEND_PATH_TO_ADDRESS
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
        address: "${user_service_url}"
        path_translation: APPEND_PATH_TO_ADDRESS
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
        address: "${user_service_url}/v1/user"
      parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              name:
                type: string
              email:
                type: string
      responses:
        201:
          description: "User created successfully"