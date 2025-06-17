# Mental Health Chat API

A FastAPI-based mental health companion chatbot that provides empathetic responses and tracks user mood dimensions.

## Features

- **Mental Health Focused**: Specialized AI responses for mental health support
- **Mood Tracking**: Analyzes and tracks 8 different mood dimensions
- **Conversation Management**: Full conversation history and management
- **Conversation Analysis**: Automatic and manual conversation scoring and analysis
- **Rate Limiting**: Configurable rate limits for free and paid users
- **Structured Responses**: Consistent JSON response format

## Database Schema

The API uses the following Supabase schema:

### Conversations Table

```sql
CREATE TABLE chat.conversations (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  title text,
  conversation_scores jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone,
  CONSTRAINT conversations_pkey PRIMARY KEY (id),
  CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_profiles(user_id)
);
```

### Messages Table

```sql
CREATE TABLE chat.messages (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  conversation_id uuid NOT NULL,
  user_id uuid NOT NULL,
  user_input text NOT NULL,
  bot_response jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT messages_pkey PRIMARY KEY (id),
  CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES chat.conversations(id)
);
```

## Mood Dimensions

The bot analyzes and tracks 8 mood dimensions:

- **mood**: float between [-5, 5] (negative = sad/depressed, positive = happy/positive)
- **stress**: float between [0, 10] (0 = no stress, 10 = extremely stressed)
- **anxiety**: float between [0, 10] (0 = no anxiety, 10 = extremely anxious)
- **energy**: float between [0, 10] (0 = no energy, 10 = very energetic)
- **motivation**: float between [0, 10] (0 = no motivation, 10 = very motivated)
- **loneliness**: float between [0, 10] (0 = not lonely, 10 = very lonely)
- **confidence**: float between [0, 10] (0 = no confidence, 10 = very confident)
- **hope**: float between [0, 10] (0 = no hope, 10 = very hopeful)

## Conversation Analysis

The API automatically analyzes conversations and stores insights in the `conversation_scores` column:

### Automatic Analysis

- Triggers every 5 messages in a conversation
- Analyzes the last 10 messages using OpenAI
- Runs in the background without blocking user responses

### Manual Analysis

- Can be triggered via API endpoint
- Useful for immediate analysis when needed

### Analysis Output

```json
{
  "overall_mood_trend": "improving|declining|stable|fluctuating",
  "key_concerns": ["array of main concerns identified"],
  "progress_indicators": ["array of positive progress indicators"],
  "recommendations": ["array of recommendations for continued support"],
  "risk_level": "low|medium|high",
  "engagement_level": "low|medium|high",
  "summary": "2-3 sentence summary of the conversation and user's state"
}
```

## API Endpoints

### 1. Create Conversation

**POST** `/conversations/`

Creates a new conversation and sends the first message.

**Request Body:**

```json
{
  "title": "Optional conversation title",
  "first_message": "User's first message"
}
```

**Query Parameters:**

- `user_id` (required): User's unique identifier
- `is_paid` (optional): Boolean for rate limiting (default: false)

**Response:**

```json
{
  "conversation": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  },
  "chat_response": {
    "content": "Bot's supportive response",
    "mood": 2.5
  }
}
```

### 2. Send Message

**POST** `/messages/`

Sends a message to an existing conversation. Automatically triggers conversation analysis every 5 messages.

**Request Body:**

```json
{
  "user_input": "User's message",
  "conversation_id": "uuid"
}
```

**Query Parameters:**

- `user_id` (required): User's unique identifier
- `is_paid` (optional): Boolean for rate limiting (default: false)

**Response:**

```json
{
  "content": "Bot's supportive response",
  "mood": 2.5
}
```

### 3. Analyze Conversation

**POST** `/conversations/{conversation_id}/analyze`

Manually trigger conversation analysis and update scores.

**Query Parameters:**

- `user_id` (required): User's unique identifier

**Response:**

```json
{
  "message": "Conversation analysis completed successfully",
  "conversation_scores": {
    "overall_mood_trend": "improving",
    "key_concerns": ["stress", "anxiety"],
    "progress_indicators": ["showing self-awareness"],
    "recommendations": ["continue therapy", "practice mindfulness"],
    "risk_level": "low",
    "engagement_level": "high",
    "summary": "User shows improvement in mood and engagement."
  }
}
```

### 4. Get Conversation Scores

**GET** `/conversations/{conversation_id}/scores`

Retrieves conversation analysis scores.

**Query Parameters:**

- `user_id` (required): User's unique identifier

**Response:**

```json
{
  "conversation_scores": {
    "overall_mood_trend": "improving",
    "key_concerns": ["stress", "anxiety"],
    "progress_indicators": ["showing self-awareness"],
    "recommendations": ["continue therapy", "practice mindfulness"],
    "risk_level": "low",
    "engagement_level": "high",
    "summary": "User shows improvement in mood and engagement."
  }
}
```

### 5. Get Conversation Messages

**GET** `/conversations/{conversation_id}/messages`

Retrieves all messages for a specific conversation.

**Query Parameters:**

- `user_id` (required): User's unique identifier

**Response:**

```json
[
  {
    "id": 1,
    "conversation_id": "uuid",
    "user_id": "uuid",
    "user_input": "User's message",
    "bot_response": {
      "content": "Bot's response",
      "mood_dimensions": {
        "mood": 2.5,
        "stress": 6.0,
        "anxiety": 4.0,
        "energy": 3.0,
        "motivation": 5.0,
        "loneliness": 2.0,
        "confidence": 4.0,
        "hope": 6.0
      }
    },
    "created_at": "timestamp"
  }
]
```

### 6. Get User Conversations

**GET** `/conversations/`

Retrieves all conversations for a user.

**Query Parameters:**

- `user_id` (required): User's unique identifier

**Response:**

```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "conversation_scores": {
      "overall_mood_trend": "improving",
      "key_concerns": ["stress"],
      "progress_indicators": ["engagement"],
      "recommendations": ["continue therapy"],
      "risk_level": "low",
      "engagement_level": "high",
      "summary": "User shows improvement."
    },
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
]
```

## Rate Limiting

- **Free Users**: 20 messages per hour
- **Paid Users**: 50 messages per hour

## Environment Variables

Create a `.env` file with the following variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables
4. Run the application:
   ```bash
   python app.py
   ```

## Testing

Run the test script to verify the API functionality:

```bash
python test_api.py
```

The test script includes:

- Conversation creation
- Message sending
- Automatic conversation analysis (every 5 messages)
- Manual conversation analysis
- Score retrieval
- Message history

## Bot Response Format

The bot stores complete responses in the database with the following structure:

```json
{
  "content": "Supportive response text",
  "mood_dimensions": {
    "mood": 2.5,
    "stress": 6.0,
    "anxiety": 4.0,
    "energy": 3.0,
    "motivation": 5.0,
    "loneliness": 2.0,
    "confidence": 4.0,
    "hope": 6.0
  }
}
```

The API returns only the `content` and `mood` (from mood_dimensions) to the user for simplicity.

## Conversation Analysis Features

### Automatic Triggers

- Analysis runs every 5 messages in a conversation
- Uses the last 10 messages for context
- Runs in background without blocking user responses

### Analysis Insights

- **Mood Trends**: Tracks overall emotional trajectory
- **Key Concerns**: Identifies recurring themes and issues
- **Progress Indicators**: Highlights positive developments
- **Risk Assessment**: Evaluates potential risk levels
- **Engagement Level**: Measures user participation
- **Recommendations**: Suggests next steps for support

### Manual Analysis

- Can be triggered on-demand via API
- Useful for immediate insights
- Same analysis quality as automatic triggers

## Error Handling

The API includes comprehensive error handling for:

- Rate limit exceeded
- Invalid conversation IDs
- Database connection issues
- OpenAI API errors
- JSON parsing errors
- Conversation analysis failures

## Security

- CORS enabled for cross-origin requests
- Rate limiting to prevent abuse
- User-specific data isolation
- Input validation using Pydantic models
- Conversation ownership verification
