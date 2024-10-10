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

  /v1/user/{user_id}/agent/{agent_id}:
    get:
      operationId: "getAgentById"
      x-google-backend:
        address: "${agent_service_url}"
        path_translation: APPEND_PATH_TO_ADDRESS
      parameters:
        - name: user_id
          in: path
          required: true
          type: string
        - name: agent_id
          in: path
          required: true
          type: string
      responses:
        200:
          description: "Successful response"
          schema:
            type: object
            properties:
              vendor:
                type: string
              name:
                type: string
              description:
                type: string
        404:
          description: "Agent not found"

  /v1/user/{user_id}/agent:
    post:
      operationId: "createAgent"
      x-google-backend:
        address: "${agent_service_url}"
        path_translation: APPEND_PATH_TO_ADDRESS
      parameters:
        - name: user_id
          in: path
          required: true
          type: string
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              user_id:
                type: string
              vendor:
                type: string
              name:
                type: string
              description:
                type: string
      responses:
        201:
          description: "Agent created successfully"
          schema:
            type: object
            properties:
              agent_id:
                type: string
        400:
          description: "Bad Request"

  /v1/user/{user_id}/agent/{agent_id}:
    delete:
      operationId: "deleteAgentById"
      x-google-backend:
        address: "${agent_service_url}"
        path_translation: APPEND_PATH_TO_ADDRESS
      parameters:
        - name: user_id
          in: path
          required: true
          type: string
        - name: agent_id
          in: path
          required: true
          type: string
      responses:
        204:
          description: "No Content"
        404:
          description: "Agent not found"