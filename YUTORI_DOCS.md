# Overview

> Build reliable web agents with the Yutori API

[Yutori](https://yutori.com/) builds web agents — agents that can reliably and autonomously execute tasks on the web.
These capabilities underpin the upcoming shift in how people interact with the web — from manual browsing to delegating
tasks to agents that operate the web for you.

We offer four APIs -- [**n1**](#n1-api), [**Browsing**](#browsing-api), [**Research**](#research-api), and [**Scouting**](#scouting-api).

Recent technical blogs from us:

* [Navigator](https://yutori.com/blog/introducing-navigator), our most accurate and efficent web navigation agent.
* [The bitter lesson for web agents](https://yutori.com/blog/the-bitter-lesson-for-web-agents), and how vision scales better than the DOM.

***

## n1 API

n1 is a pixels-to-actions large language model designed to interact with webpages in browser environments.
It processes the user’s instruction, the current screenshot, and the history of previous actions and screenshots, to predict the next action — click, type, scroll, etc.

It follows OpenAI's Chat Completions interface.

See [n1 API](/reference/n1) to get started.

If you don’t want to manage your own browser infra, see the [Browsing API](/reference/browsing-create)
that calls n1 on our cloud browser.

***

## Browsing API

The Browsing API enables automation of browser-based workflows.

Simply describe your browser-based task in natural language, for example:

* Fill a form on website
* Check a webpage for changes and retrieve updated information
* Check multiple webpages and download a summary in a structured format
* Log into a website and enter or update information

and an AI agent that runs its own cloud browser and
operates it like a person will click, type, scroll, and navigate for you.

For login/signup or other auth-heavy flows, we recommend setting `"require_auth": true` on your request so the system can prefer an auth-optimized browser provider.

See the [Browsing API](/reference/browsing-create) to create your first browsing task.

***

## Research API

The Research API enables one-time (wide and deep) research of anything on the web.

Simply specify what you want to research in natural language, for example:

* What are the latest developments in quantum computing?
* Summarize recent AI model launches and their capabilities
* Research competitor pricing for cloud GPU instances

<Note>
  Unlike the Browsing API (which uses a single navigator), Research API uses 100+ MCP tools for comprehensive web-based research.
  This provides the same research capabilities as the Scouting API, but without scheduling recurring runs.
</Note>

See the [Research API](/reference/research-create) to create your first research task.

***

## Scouting API

The Scouting API enables continuous monitoring of the web at a
configurable schedule for tracking any changes relevant to a query.

Simply specify what you're looking to track in natural language, for example:

* anytime a startup in SF announces seed funding
* when H100 pricing per hour drops below \$1.50
* when a new AI model launches

and a 'Scout' will spin up a team of sub-agents to monitor --
either specific URLs or the entire web -- and alert you with structured data whenever there's a relevant update.

<Note>
  While the Browsing and Research APIs are designed for one-time task execution -- either by a single navigator in a cloud browser or
  by a multi-agent system -- the Scouting API is meant for setting up periodic monitoring
  and alerts for changes over time.
</Note>

See the [Scouting API](/reference/scouts-create) to create your first scouting task.

***

The Scouting API powers Yutori's [Scouts](https://yutori.com/product) product. See how it works:

<iframe className="w-full aspect-video rounded-xl" src="https://www.youtube.com/embed/8-wQEeJobsM" title="YouTube video player" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.yutori.com/llms.txt



# Create A Task

> Launches a one-time wide and deep research task on the web.

<RequestExample>
  ```bash cURL theme={null}
  curl --request POST \
    --url https://api.yutori.com/v1/research/tasks \
    --header 'X-API-Key: YOUR_API_KEY' \
    --header 'Content-Type: application/json' \
    --data '{
      "query": "What are the latest developments in quantum computing from the past week? Include company announcements, research papers, and product releases."
    }'
  ```

  ```python Python theme={null}
  import requests

  response = requests.post(
      "https://api.yutori.com/v1/research/tasks",
      headers={"X-API-Key": "YOUR_API_KEY"},
      json={
          "query": "What are the latest developments in quantum computing from the past week? Include company announcements, research papers, and product releases."
      }
  )
  print(response.json())
  ```

  ```javascript JavaScript theme={null}
  const response = await fetch("https://api.yutori.com/v1/research/tasks", {
    method: "POST",
    headers: {
      "X-API-Key": "YOUR_API_KEY",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      query: "What are the latest developments in quantum computing from the past week? Include company announcements, research papers, and product releases."
    })
  });
  const data = await response.json();
  ```
</RequestExample>

## Advanced Example

<Accordion title="Using Webhooks & a Structured Output Schema">
  Get webhook notifications and structured JSON output for easier parsing.

  <CodeGroup>
    ```bash cURL theme={null}
    curl --request POST \
      --url https://api.yutori.com/v1/research/tasks \
      --header 'X-API-Key: YOUR_API_KEY' \
      --header 'Content-Type: application/json' \
      --data '{
        "query": "What are the latest developments in quantum computing from the past week? Include company announcements, research papers, and product releases.",
        "user_timezone": "America/Los_Angeles",
        "webhook_url": "https://example.com/webhook",
        "task_spec": {
          "output_schema": {
            "type": "json",
            "json_schema": {
              "type": "object",
              "properties": {
                "developments": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "title": { "type": "string" },
                      "summary": { "type": "string" },
                      "source_url": { "type": "string" },
                      "category": { "type": "string", "enum": ["company", "research", "product"] }
                    },
                    "required": ["title", "summary", "source_url"]
                  }
                }
              },
              "required": ["developments"]
            }
          }
        }
      }'
    ```

    ```python Python theme={null}
    import requests

    response = requests.post(
        "https://api.yutori.com/v1/research/tasks",
        headers={"X-API-Key": "YOUR_API_KEY"},
        json={
            "query": "What are the latest developments in quantum computing from the past week? Include company announcements, research papers, and product releases.",
            "user_timezone": "America/Los_Angeles",
            "webhook_url": "https://example.com/webhook",
            "task_spec": {
                "output_schema": {
                    "type": "json",
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "developments": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "summary": {"type": "string"},
                                        "source_url": {"type": "string"},
                                        "category": {"type": "string", "enum": ["company", "research", "product"]}
                                    },
                                    "required": ["title", "summary", "source_url"]
                                }
                            }
                        },
                        "required": ["developments"]
                    }
                }
            }
        }
    )
    print(response.json())
    ```

    ```javascript JavaScript theme={null}
    const response = await fetch("https://api.yutori.com/v1/research/tasks", {
      method: "POST",
      headers: {
        "X-API-Key": "YOUR_API_KEY",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: "What are the latest developments in quantum computing from the past week? Include company announcements, research papers, and product releases.",
        user_timezone: "America/Los_Angeles",
        webhook_url: "https://example.com/webhook",
        task_spec: {
          output_schema: {
            type: "json",
            json_schema: {
              type: "object",
              properties: {
                developments: {
                  type: "array",
                  items: {
                    type: "object",
                    properties: {
                      title: { type: "string" },
                      summary: { type: "string" },
                      source_url: { type: "string" },
                      category: { type: "string", enum: ["company", "research", "product"] }
                    },
                    required: ["title", "summary", "source_url"]
                  }
                }
              },
              required: ["developments"]
            }
          }
        }
      })
    });
    const data = await response.json();
    ```
  </CodeGroup>
</Accordion>


## OpenAPI

````yaml POST /v1/research/tasks
openapi: 3.1.0
info:
  title: FastAPI
  version: 0.1.0
servers:
  - url: https://api.yutori.com
    description: Production
security:
  - ApiKeyAuth: []
paths:
  /v1/research/tasks:
    post:
      tags:
        - Research
      summary: Create A Task
      description: Launches a one-time wide and deep research task on the web.
      operationId: create_research_task_v1_research_tasks_post
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateResearchTaskRequest'
        required: true
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateResearchTaskResponse'
        '422':
          description: Validation Error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
components:
  schemas:
    CreateResearchTaskRequest:
      properties:
        query:
          type: string
          title: Query
          description: |2-

                    String describing the research task in natural language.
                    
          examples:
            - >-
              What are the latest developments in quantum computing from the
              past week?
        user_timezone:
          type: string
          title: User Timezone
          description: >-
            User's timezone for contextual awareness (e.g.
            'America/Los_Angeles')
          default: America/Los_Angeles
          examples:
            - America/Los_Angeles
        user_location:
          anyOf:
            - type: string
            - type: 'null'
          title: User Location
          description: >-
            User's coarse location in the format: city, region_code,
            country_name
          default: San Francisco, CA, US
          examples:
            - San Francisco, CA, US
        task_spec:
          anyOf:
            - $ref: '#/components/schemas/TaskSpec'
            - type: 'null'
          description: Task specification with JSON output schema for structured results
          examples:
            - output_schema:
                json_schema:
                  properties:
                    developments:
                      items:
                        properties:
                          title:
                            description: Title of the development
                            type: string
                          summary:
                            description: Brief summary
                            type: string
                          source:
                            description: URL for more details
                            type: string
                        required:
                          - title
                          - summary
                          - source
                        type: object
                      type: array
                  required:
                    - developments
                  type: object
                type: json
        webhook_url:
          anyOf:
            - type: string
            - type: 'null'
          title: Webhook Url
          description: >-
            Optional webhook URL to receive results when the research task
            completes
          examples:
            - https://example.com/webhook
        webhook_format:
          type: string
          enum:
            - scout
            - slack
            - zapier
          title: Webhook Format
          description: Webhook payload format. Slack incoming webhook URLs require 'slack'.
          default: scout
          examples:
            - scout
      type: object
      required:
        - query
      title: CreateResearchTaskRequest
    CreateResearchTaskResponse:
      properties:
        task_id:
          type: string
          title: Task Id
          description: Unique identifier for this research task
        view_url:
          type: string
          title: View Url
          description: URL to view task progress and results
        status:
          type: string
          enum:
            - queued
            - running
            - succeeded
            - failed
          title: Status
          description: Current status of the research task
        webhook_url:
          anyOf:
            - type: string
            - type: 'null'
          title: Webhook Url
          description: Echoes the webhook URL configured for this task, if provided
      type: object
      required:
        - task_id
        - view_url
        - status
      title: CreateResearchTaskResponse
      description: Response for creating a research task.
    HTTPValidationError:
      properties:
        detail:
          items:
            $ref: '#/components/schemas/ValidationError'
          type: array
          title: Detail
      type: object
      title: HTTPValidationError
    TaskSpec:
      properties:
        output_schema:
          anyOf:
            - $ref: '#/components/schemas/JsonSchemaSpec'
            - type: 'null'
      type: object
      title: TaskSpec
    ValidationError:
      properties:
        loc:
          items:
            anyOf:
              - type: string
              - type: integer
          type: array
          title: Location
        msg:
          type: string
          title: Message
        type:
          type: string
          title: Error Type
      type: object
      required:
        - loc
        - msg
        - type
      title: ValidationError
    JsonSchemaSpec:
      properties:
        type:
          type: string
          const: json
          title: Type
          default: json
        json_schema:
          additionalProperties: true
          type: object
          title: Json Schema
          description: A JSON Schema object defining the structure
      type: object
      required:
        - json_schema
      title: JsonSchemaSpec
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      name: x-api-key
      in: header

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.yutori.com/llms.txt