# Cloud-AI

## Introduction

Cloud-AI is an advanced AI tool that revolutionizes code generation through natural language instruction. Powered by a cooperative system of multiple Large Language Model (LLM) agents, Cloud-AI offers a comprehensive solution for automating software development processes.

### Key Features:

- **Holistic Repository Understanding**: Cloud-AI can comprehend and analyze entire code repositories.
- **Dynamic File Management**: Create new folders and files based on user queries.
- **Multi-Source Code Updates**: Implement changes across multiple source files from a single feature request.
- **Self-Correction Mechanism**: Automatically or manually correct mistakes based on internal agent feedback or external input.
- **Integrated Development Environment**: Features a frontend chatbox embedded in VS Code for seamless user interaction.
- **Command-Line Interface**: Provides various commands for programmatic interaction with the repository.
- **External Tool Integration**: Designed for easy integration with various external tools to automate the entire software development lifecycle.

## Demo: AWS Landing Zone Deployment

Our demo showcases the deployment of an AWS landing zone utilizing three LLM agents without any manual coding.

### Demo Resources:
- [Video Demonstration](https://www.youtube.com/watch?v=V5R5hro-Dzw)
- [Chat History](https://drive.google.com/file/d/1CsrIgSV1GWur_AVt_u7sj4KP56jzUNr6/view?usp=sharing)

### Key Highlights:
1. **Zero-Code Deployment**: The entire infrastructure was deployed without writing a single line of code manually.
2. **Natural Language Instructions**: We provided Cloud-AI with a detailed description of the desired AWS infrastructure using natural language.
3. **Multi-Agent Collaboration**: Three specialized agents - Coordinator, Code, and CICD - communicated effectively to complete the task.
4. **Dynamic Workflow**: The workflow among agents was not predefined but dynamically determined based on previous agent outputs and external tool inputs.

### Demo Query:

<details>
<summary>Click to expand demo query</summary>

```
Hello, I'm seeking your expertise as a DevOps and Cloud Engineer. I plan to deploy an application on AWS using EC2 instances and require your 
help to develop two specific AWS Terraform modules from scratch—no external pre-built modules allowed.

1. VPC Module: Please create a module for a Virtual Private Cloud (VPC).
2. EC2 Module: This module should include an autoscaling group, an application load balancer, and a security group to efficiently manage a fleet 
of EC2 instances. Configure the EC2 instances to use the AMI ID "ami-0b0ea68c435eb488d" and include a simple userdata script that sets up a 
homepage with the message "Auto Deployment from Cloud-AI".

For each module, ensure the following files are included: main.tf, variables.tf, and outputs.tf.

Additionally, create root files (included: main.tf, variables.tf, and outputs.tf at the project root level) that integrates these two modules to 
set up the infrastructure. This configuration should invoke the VPC and EC2 modules, ensuring that they work together to deploy the application.
Provide default values for all the variables defined in variables.tf.

Ensure the application can be accessed through the ALB DNS, and that visitors to the site will see the message "Auto Deployment from Cloud-AI" 
displayed on the webpage.

Please proceed to deploy my application using these modules and provide the executable Terraform codes along with a clear folder structure 
to organize these modules and deployment scripts.
```
</details>

## Infrastructure

The primary Cloud-AI infrastructure is hosted on Google Cloud Platform (GCP).

### Future Plans:
- Implementation of a multi-cloud solution
- Active-active configuration and disaster failover between GCP and AWS

### Architecture:
- Primarily utilizes serverless services
- Implements an event-driven design

![Cloud-AI Infrastructure Diagram](media/image4.png)

## Cloud Runs

### Orchestrator
Manages the overall reasoning and decision-making process. It determines the next step among three possibilities:
1. Send the message to a third-party endpoint via llm-request-queue pub/sub
2. Gather more context before sending via vector-search-queue pub/sub
3. Complete the current chat round via completion-queue pub/sub

### Data Processor
Responsibilities:
1. Process files by embedding their content using an external LLM API
2. Save original files to Cloud Storage, metadata to Firestore, and embeddings to Google Cloud's Vertex AI VectorSearch
3. Return processed files to users for local repository updates

### Vector Search
When additional context is needed:
1. Contact the frontend for more context
2. Send the message with enriched context to llm-request-queue

### LLM Communicator
Manages communication with external LLM APIs:
1. Send messages to the LLM
2. Process responses
3. Publish processed messages to the pending-reasoning-queue Pub/Sub topic

### Thread
Responsible for initiating or continuing conversations.

## Pub/Sub Topics

### pending-reasoning-topic
- **Purpose**: Stores intermediate messages processed by LLM Communicator
- **Usage**: Orchestrator periodically checks this topic to continue the reasoning process

### completion-topic
- **Purpose**: Stores messages identified as complete for the current query cycle
- **Usage**: LLM Communicator processes messages from this topic to complete file-related tasks

### vector-search-topic
- **Purpose**: Contains requests for vector similarity searches
- **Usage**: Vector Search processes messages, gathers more context from the frontend, and adds enriched messages to llm-request-topic

### llm-request-topic
- **Purpose**: Stores messages ready to be sent to external LLM APIs
- **Usage**: LLM Communicator picks up these messages and sends them to the LLM service

## Storage

- **Firestore**: Stores metadata for chat history, user information, and AI agent information
- **Cloud Storage (Bucket)**: Stores the actual chat history

## Frontend

### Chatbox
An embedded chatbox built into Microsoft Visual Studio Code, featuring:
1. Repository scanning to create high-dimensional vectors
2. Access to all source code files in the current repository
3. Automatic file updates from the backend
4. User-friendly UI for code manipulation via natural language

![Cloud-AI Chatbox](media/image2.png)

### Vector File
Stores embedding vector data of files in the repository.

### FileProcessor
Frontend component responsible for handling requests from backend services:
1. Respond to Vector Search requests by searching and sending more context
2. Update source codes and their embedding vector file based on Data Processor requests

## Backend

The backend consists of four microservices: User, Agent, Context, and Vector. Each microservice is responsible for CRUD operations on its corresponding entities.

![Backend Entity Relationships](media/image1.png)

### Backend Entities Overview

1. **User**: Represents individuals interacting with the system. Users can create agents, contexts, start conversations (threads), and send/receive messages.

2. **Agent**: Virtual AI bots created by users. Agents specialize in particular domains and participate in conversations with users, either individually or in groups.

3. **Context**: Provides the scenario or theme for conversations (threads). It tracks key information and participants (users and agents) involved in discussions.

4. **Thread**: Represents specific conversations between users and agents within a particular context. Threads contain all exchanged messages.

5. **Message**: Individual communications exchanged within a thread. Messages can be from users or agents and include metadata like timestamps and content previews.

### Entity Relationships

- **User-Agent**: Users create and manage agents. Agents are bound to their creators and specialize in specific domains.
- **User-Context**: Users can create multiple contexts, each representing a unique scenario. Contexts serve as containers for multiple threads.
- **User-Thread**: Users initiate threads within contexts. Threads capture interactions between users and agents.
- **Thread-Message**: Threads comprise multiple messages exchanged between users and agents, maintaining chronological order and metadata.
- **Context-Thread**: Contexts hold one or more threads, allowing ongoing conversations linked to the same overarching topic.

## API Endpoints

### User Endpoints

#### GET /v1/user/{user_id}
Retrieves an existing user's information.

**Response:**
```json
{
  "user_id": "user_id_1",
  "name": "Alice",
  "email": "alice@example.com",
  "last_active": "2024-09-25T10:30:00Z"
}
```

**Status Codes:**
- 200: OK
- 404: User not found

#### POST /v1/user
Creates a new user.

**Request Body:**
```json
{
  "name": "Bob",
  "email": "bob@example.com"
}
```

**Response:**
```json
{
  "user_id": "user_id_1"
}
```

**Status Codes:**
- 201: Created
- 400: Bad Request

#### PUT /v1/user/{user_id}
Updates an existing user's information.

**Request Body:**
```json
{
  "name": "Alice Smith",
  "email": "alice.smith@example.com"
}
```

**Status Codes:**
- 200: OK
- 404: User not found

#### DELETE /v1/user/{user_id}
Deletes an existing user.

**Status Codes:**
- 204: No Content
- 404: User not found

### Agent Endpoints

#### GET /v1/user/{user_id}/agent/{agent_id}
Retrieves an existing agent's information.

**Response:**
```json
{
  "agent_id": "agent_id_1",
  "user_id": "user_id_1",
  "vendor": "OpenAI",
  "vendor_agent_id": "vendor_agent_id_1",
  "name": "TravelBot",
  "description": "An AI agent specialized in travel planning, providing personalized itineraries and recommendations based on user preferences."
}
```

**Status Codes:**
- 200: OK
- 404: Agent not found

#### POST /v1/user/{user_id}/agent
Creates a new agent.

**Request Body:**
```json
{
  "name": "FinanceBot",
  "vendor": "OpenAI",
  "description": "An AI agent specialized in personal finance and investment advice."
}
```

**Response:**
```json
{
  "vendor_agent_id": "vendor_agent_id_1"
}
```

**Status Codes:**
- 201: Created
- 400: Bad Request

#### DELETE /v1/user/{user_id}/agent/{agent_id}
Deletes an existing agent.

**Status Codes:**
- 204: No Content
- 404: Agent not found

### Thread Endpoints

#### GET /v1/user/{user_id}/thread/{thread_id}
Retrieves an existing thread's information.

**Response:**
```json
{
  "thread_id": "thread_id_1",
  "user_id": "user_id_1",
  "context_id": "context_id_1",
  "participants": ["user_id_1", "vendor_agent_id_1", "vendor_agent_id_2"],
  "vendor": "OpenAI",
  "vendor_thread_id": "vendor_thread_id_1",
  "created_at": "2024-09-25T10:00:00Z",
  "last_message_at": "2024-09-25T10:30:00Z",
  "messages": [
    {
      "message_id": "msg_1",
      "user_id": "user_id_1",
      "timestamp": "2024-09-25T10:00:00Z",
      "content_preview": "I'm thinking about visiting Paris and Rome...",
      "storage_path": "contexts/context_id_1/threads/thread_id_1/messages/msg_1.txt"
    },
    {
      "message_id": "msg_2",
      "user_id": "agent_id_1",
      "timestamp": "2024-09-25T10:30:00Z",
      "content_preview": "Great choice! Paris and Rome are both...",
      "storage_path": "contexts/context_id_1/threads/thread_id_1/messages/msg_2.txt"
    }
  ]
}
```

**Status Codes:**
- 200: OK
- 404: Thread not found

#### POST /v1/user/{user_id}/thread
Creates a new thread.

**Request Body:**
```json
{
  "context_id": "context_id_1",
  "context": "...........",
  "vendor": "OpenAI"
}
```

**Response:**
```json
{
  "thread_id": "thread_id_1",
  "vendor": "OpenAI",
  "vendor_thread_id": "vendor_thread_id_1"
}
```

**Status Codes:**
- 201: Created
- 400: Bad Request

#### DELETE /v1/user/{user_id}/thread/{thread_id}
Deletes an existing thread.

**Status Codes:**
- 204: No Content
- 404: Thread not found

### Message Endpoints

#### GET /v1/user/{user_id}/thread/{thread_id}/message/{message_id}
Retrieves an existing message's information.

**Response:**
```json
{
  "message_id": "msg_1",
  "thread_id": "thread_id_1",
  "user_id": "user_id_1",
  "content": "I'm thinking about visiting Paris and Rome for my upcoming vacation. I have about 10 days and I'm interested in historical sites, local cuisine, and maybe some art museums. Can you help me plan this trip?",
  "timestamp": "2024-09-25T10:00:00Z",
  "type": "text",
  "metadata": {
    "client_info": "Web browser",
    "ip_address": "192.168.1.1"
  }
}
```

**Status Codes:**
- 200: OK
- 404: Message not found

#### POST /v1/user/{user_id}/thread/{thread_id}/message
Continues the chat by adding a new message to the thread.

**Request Body:**
```json
{
  "content": "That sounds like a great plan! Let's start by discussing your preferences for Paris.",
  "user_id": "agent_id_1",
  "vendor": "OpenAI",
  "vendor_thread_id": "vendor_thread_id_1",
  "type": "text"
}
```

**Status Codes:**
- 201: Created
- 400: Bad Request

### Context Endpoints

#### GET /v1/user/{user_id}/context/{context_id}
Retrieves an existing context's information.

**Response:**
```json
{
  "context_id": "context_id_1",
  "user_id": "user_id_1",
  "scenario": "User is planning a vacation to Europe",
  "participants": ["user_id_1", "agent_id_1", "agent_id_2"],
  "created_at": "2024-09-25T09:00:00Z",
  "last_updated_at": "2024-09-25T10:30:00Z"
}
```

**Status Codes:**
- 200: OK
- 404: Context not found

#### POST /v1/user/{user_id}/context
Creates a new context.

**Request Body:**
```json
{
  "scenario": "User is planning a business trip to Asia",
  "participants": ["user_id_1", "agent_id_3"]
}
```

**Status Codes:**
- 201: Created
- 400: Bad Request

#### DELETE /v1/user/{user_id}/context/{context_id}
Deletes an existing context.

**Status Codes:**
- 204: No Content
- 404: Context not found

## Agents

Cloud-AI utilizes three specialized AI agents to facilitate the development process:

1. **COORDINATOR_AGENT**: Manages communication flow between different AI agents within the chatroom environment. It analyzes chat history and directs tasks to appropriate assistants based on context and user needs.

2. **CODE_AGENT**: A retrieve-augmented coding agent that generates and updates code based on user requirements and provided context. It follows strict formatting guidelines to maintain consistency and clarity in code updates.

3. **EXTERNAL_INFO_MONITOR_AGENT**: Monitors and analyzes various external outputs related to the software development lifecycle, including test tool outputs, CICD logs, and local build results.

Each agent has specific responsibilities and communication protocols to ensure smooth collaboration and efficient task completion.

## Getting Started

(Add instructions for setting up and using Cloud-AI here)

## Contributing

(Add guidelines for contributing to the Cloud-AI project here)

## License

(Add license information here)

## Contact

(Add contact information or links to support channels here)
