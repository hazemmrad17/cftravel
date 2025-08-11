import requests
import json

def test_chat_formatting():
    url = "http://localhost:8001/chat"
    headers = {"Content-Type": "application/json"}
    
    # Test message
    data = {
        "message": "Bonjour",
        "conversation_id": "test-formatting-123"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print("=== AI Response ===")
            print(result.get("response", "No response"))
            print("==================")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat_formatting() 