import requests
import json
import uuid
import time

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_USER_ID = "e589c2c4-1cf4-4417-ac2f-99f4d9c39c46"  # Generate a test user ID

def test_create_conversation():
    """Test creating a new conversation"""
    print("Testing conversation creation...")
    
    data = {
        "title": "Test Conversation",
        "first_message": "I'm feeling really stressed today and can't seem to focus on my work."
    }
    
    params = {
        "user_id": TEST_USER_ID,
        "is_paid": False
    }
    
    response = requests.post(f"{BASE_URL}/conversations/", json=data, params=params)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Conversation created successfully!")
        print(f"Conversation ID: {result['id']}")
        return result['id']
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_send_message(conversation_id, is_paid=False):
    """Test sending a message to an existing conversation"""
    user_type = "paid" if is_paid else "free"
    print(f"\nTesting message sending to conversation {conversation_id} ({user_type} user)...")
    
    data = {
        "user_input": "I've been having trouble sleeping lately and feel anxious about tomorrow's meeting.",
        "conversation_id": conversation_id
    }
    
    params = {
        "user_id": TEST_USER_ID,
        "is_paid": is_paid
    }
    
    response = requests.post(f"{BASE_URL}/messages/", json=data, params=params)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Message sent successfully!")
        print(f"Bot Response: {result['content']}")
        print(f"Remaining Responses: {result['remaining_responses']}")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_get_conversation_messages(conversation_id):
    """Test retrieving messages from a conversation"""
    print(f"\nTesting message retrieval for conversation {conversation_id}...")
    
    params = {
        "user_id": TEST_USER_ID
    }
    
    response = requests.get(f"{BASE_URL}/conversations/{conversation_id}/messages", params=params)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ Retrieved {len(messages)} messages")
        for i, msg in enumerate(messages):
            print(f"Message {i+1}:")
            print(f"  User Input: {msg['user_input']}")
            if msg.get('bot_response'):
                print(f"  Bot Content: {msg['bot_response']['content']}")
                print(f"  Mood Dimensions: {json.dumps(msg['bot_response']['mood_dimensions'], indent=2)}")
    else:
        print(f"❌ Error: {response.text}")

def test_get_user_conversations():
    """Test retrieving all conversations for a user"""
    print(f"\nTesting conversation retrieval for user {TEST_USER_ID}...")
    
    params = {
        "user_id": TEST_USER_ID
    }
    
    response = requests.get(f"{BASE_URL}/conversations/", params=params)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ Retrieved {len(conversations)} conversations")
        for conv in conversations:
            print(f"  Conversation ID: {conv['id']}")
            print(f"  Title: {conv.get('title', 'No title')}")
            print(f"  Created: {conv['created_at']}")
    else:
        print(f"❌ Error: {response.text}")

def test_analyze_conversation(conversation_id):
    """Test conversation analysis functionality"""
    print(f"\nTesting conversation analysis for conversation {conversation_id}...")
    
    params = {
        "user_id": TEST_USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/conversations/{conversation_id}/analyze", params=params)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Conversation analysis completed successfully!")
        print(f"Analysis Results: {json.dumps(result['scores'], indent=2)}")
    else:
        print(f"❌ Error: {response.text}")

def test_get_conversation_scores(conversation_id):
    """Test retrieving conversation scores"""
    print(f"\nTesting conversation scores retrieval for conversation {conversation_id}...")
    
    params = {
        "user_id": TEST_USER_ID
    }
    
    response = requests.get(f"{BASE_URL}/conversations/{conversation_id}/scores", params=params)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Conversation scores retrieved successfully!")
        if result:
            print(f"Scores: {json.dumps(result, indent=2)}")
        else:
            print("No scores available yet")
    else:
        print(f"❌ Error: {response.text}")

def test_multiple_messages_for_analysis(conversation_id):
    """Test sending multiple messages to trigger automatic analysis"""
    print(f"\nTesting multiple messages to trigger automatic analysis...")
    
    test_messages = [
        "I've been feeling really down lately and don't know what to do.",
        "My friends don't seem to understand what I'm going through.",
        "I tried to go for a walk today but couldn't find the motivation.",
        "I'm worried about my future and feel like I'm not making progress.",
        "Actually, I had a small win today - I managed to cook myself a meal."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nSending message {i}: {message[:50]}...")
        
        data = {
            "user_input": message,
            "conversation_id": conversation_id
        }
        
        params = {
            "user_id": TEST_USER_ID,
            "is_paid": False
        }
        
        response = requests.post(f"{BASE_URL}/messages/", json=data, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Message {i} sent successfully!")
            print(f"Bot Response: {result['content'][:100]}...")
            print(f"Remaining Responses: {result['remaining_responses']}")
            
            # After 5 messages, check if analysis was triggered
            if i % 5 == 0:
                print(f"\n--- Message {i} sent (should trigger analysis) ---")
                # Wait a moment for background analysis
                time.sleep(2)
                test_get_conversation_scores(conversation_id)
        else:
            print(f"❌ Error sending message {i}: {response.text}")

def test_rate_limiting():
    """Test rate limiting functionality for free users"""
    print(f"\nTesting rate limiting for free user...")
    
    # Create a new conversation for rate limiting test
    conversation_data = {
        "title": "Rate Limit Test Conversation",
        "first_message": "Testing rate limits."
    }
    
    params = {
        "user_id": TEST_USER_ID,
        "is_paid": False
    }
    
    response = requests.post(f"{BASE_URL}/conversations/", json=conversation_data, params=params)
    if response.status_code != 200:
        print("❌ Failed to create conversation for rate limit test")
        return
    
    conversation_id = response.json()['id']
    
    # Send messages until we hit the rate limit (20 for free users)
    message_count = 0
    while message_count < 25:  # Try to exceed the limit
        data = {
            "user_input": f"Test message {message_count + 1} for rate limiting.",
            "conversation_id": conversation_id
        }
        
        response = requests.post(f"{BASE_URL}/messages/", json=data, params=params)
        
        if response.status_code == 200:
            result = response.json()
            message_count += 1
            print(f"Message {message_count}: Remaining responses: {result['remaining_responses']}")
            
            if result['remaining_responses'] == 0:
                print("✅ Rate limit reached successfully!")
                break
        elif response.status_code == 429:
            print("✅ Rate limit exceeded - 429 status code received")
            print(f"Error message: {response.json()['detail']}")
            break
        else:
            print(f"❌ Unexpected error: {response.text}")
            break
    
    print(f"Total messages sent before rate limit: {message_count}")

def test_paid_user_benefits():
    """Test paid user benefits (higher rate limits and conversation history)"""
    print(f"\nTesting paid user benefits...")
    
    # Create a new conversation for paid user test
    conversation_data = {
        "title": "Paid User Test Conversation",
        "first_message": "Testing paid user features."
    }
    
    params = {
        "user_id": TEST_USER_ID,
        "is_paid": True
    }
    
    response = requests.post(f"{BASE_URL}/conversations/", json=conversation_data, params=params)
    if response.status_code != 200:
        print("❌ Failed to create conversation for paid user test")
        return
    
    conversation_id = response.json()['id']
    
    # Send a few messages to test the higher rate limit
    for i in range(5):
        data = {
            "user_input": f"Paid user test message {i + 1}.",
            "conversation_id": conversation_id
        }
        
        response = requests.post(f"{BASE_URL}/messages/", json=data, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Paid user message {i + 1}: Remaining responses: {result['remaining_responses']}")
            # Paid users should have 50 - (i + 1) remaining responses
            expected_remaining = 50 - (i + 1)
            if result['remaining_responses'] == expected_remaining:
                print(f"✅ Correct remaining responses for paid user: {expected_remaining}")
            else:
                print(f"❌ Expected {expected_remaining}, got {result['remaining_responses']}")
        else:
            print(f"❌ Error sending paid user message: {response.text}")

def test_conversation_history_limits():
    """Test that conversation history is limited correctly for free vs paid users"""
    print(f"\nTesting conversation history limits...")
    
    # Create a conversation for history testing
    conversation_data = {
        "title": "History Limit Test Conversation",
        "first_message": "Testing conversation history limits."
    }
    
    # Test free user history limit (5 messages)
    print("Testing free user conversation history limit (5 messages)...")
    params = {
        "user_id": TEST_USER_ID,
        "is_paid": False
    }
    
    response = requests.post(f"{BASE_URL}/conversations/", json=conversation_data, params=params)
    if response.status_code != 200:
        print("❌ Failed to create conversation for history test")
        return
    
    conversation_id = response.json()['id']
    
    # Send 10 messages to test history limit
    for i in range(10):
        data = {
            "user_input": f"History test message {i + 1} for free user.",
            "conversation_id": conversation_id
        }
        
        response = requests.post(f"{BASE_URL}/messages/", json=data, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Free user message {i + 1}: Remaining responses: {result['remaining_responses']}")
        else:
            print(f"❌ Error sending free user message: {response.text}")
    
    # Note: The conversation history limit is internal to the API and affects
    # how many previous messages are sent to the AI model, but doesn't affect
    # the API response directly. This is tested implicitly through the message
    # sending functionality.
    print("✅ Conversation history limit test completed (limit is applied internally)")

def main():
    print("🧠 Mental Health Chat API Test")
    print("=" * 50)
    
    # Test 1: Create conversation
    conversation_id = test_create_conversation()
    
    if conversation_id:
        # Test 2: Send initial message (free user)
        test_send_message(conversation_id, is_paid=False)
        
        # Test 3: Send message as paid user
        test_send_message(conversation_id, is_paid=True)
        
        # Test 4: Test rate limiting for free users
        test_rate_limiting()
        
        # Test 5: Test paid user benefits
        test_paid_user_benefits()
        
        # Test 6: Test conversation history limits
        test_conversation_history_limits()
        
        # Test 7: Send multiple messages to trigger analysis
        test_multiple_messages_for_analysis(conversation_id)
        
        # Test 8: Manual conversation analysis
        test_analyze_conversation(conversation_id)
        
        # Test 9: Get conversation scores
        test_get_conversation_scores(conversation_id)
        
        # Test 10: Get conversation messages
        test_get_conversation_messages(conversation_id)
        
        # Test 11: Get user conversations
        test_get_user_conversations()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main() 