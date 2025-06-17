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

def test_send_message(conversation_id):
    """Test sending a message to an existing conversation"""
    print(f"\nTesting message sending to conversation {conversation_id}...")
    
    data = {
        "user_input": "I've been having trouble sleeping lately and feel anxious about tomorrow's meeting.",
        "conversation_id": conversation_id
    }
    
    params = {
        "user_id": TEST_USER_ID,
        "is_paid": False
    }
    
    response = requests.post(f"{BASE_URL}/messages/", json=data, params=params)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Message sent successfully!")
        print(f"Bot Response: {result['content']}")
    else:
        print(f"❌ Error: {response.text}")

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
            
            # After 5 messages, check if analysis was triggered
            if i % 5 == 0:
                print(f"\n--- Message {i} sent (should trigger analysis) ---")
                # Wait a moment for background analysis
                time.sleep(2)
                test_get_conversation_scores(conversation_id)
        else:
            print(f"❌ Error sending message {i}: {response.text}")

def main():
    print("🧠 Mental Health Chat API Test")
    print("=" * 50)
    
    # Test 1: Create conversation
    conversation_id = test_create_conversation()
    
    if conversation_id:
        # Test 2: Send initial message
        test_send_message(conversation_id)
        
        # Test 3: Send multiple messages to trigger analysis
        test_multiple_messages_for_analysis(conversation_id)
        
        # Test 4: Manual conversation analysis
        test_analyze_conversation(conversation_id)
        
        # Test 5: Get conversation scores
        test_get_conversation_scores(conversation_id)
        
        # Test 6: Get conversation messages
        test_get_conversation_messages(conversation_id)
        
        # Test 7: Get user conversations
        test_get_user_conversations()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main() 