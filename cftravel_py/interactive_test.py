#!/usr/bin/env python3
"""
Interactive test script for Layla Travel Agent
Test the pipeline with your own inputs
"""

import os
import sys
from pathlib import Path

# Load environment variables before any other imports
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Verify required environment variables
if not os.getenv('GROQ_API_KEY'):
    print("❌ Error: GROQ_API_KEY not found in environment")
    print("Please set your GROQ_API_KEY in the .env file")
    sys.exit(1)

# Enable debug mode
os.environ['DEBUG'] = 'true'
print("🔍 Debug mode enabled - you'll see detailed processing information")

# Now import the rest of the application
from concrete_pipeline import LaylaConcreteAgent

def main():
    """Interactive test function"""
    print("🤖 Layla Travel Agent - Interactive Test")
    print("=" * 50)
    print("This will test the pipeline with your own inputs")
    print("Type 'quit' to exit, 'status' to see pipeline info")
    print("Type 'preferences' to see current preferences, 'clear' to reset preferences")
    print()
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize agent
        print("🔄 Initializing Layla agent...")
        agent = LaylaConcreteAgent()
        print("✅ Agent initialized successfully!")
        
        # Show status
        status = agent.get_status()
        print(f"\n📊 Pipeline Status:")
        print(f"   Reasoning Model: {status['reasoning_model']}")
        print(f"   Generation Model: {status['generation_model']}")
        print(f"   Matching Model: {status['matching_model']}")
        print(f"   Offers Loaded: {status['offers_loaded']}")
        print(f"   User Preferences: {status.get('user_preferences', {})}")
        print()
        
        # Interactive loop
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
                
            elif user_input.lower() == 'status':
                status = agent.get_status()
                preferences = agent.get_preferences()
                print(f"\n📊 Current Status:")
                print(f"   Reasoning: {status['reasoning_model']}")
                print(f"   Generation: {status['generation_model']}")
                print(f"   Matching: {status['matching_model']}")
                print(f"   Offers: {status['offers_loaded']} loaded")
                print(f"   Memory: {'✅ Enabled' if status['memory_enabled'] else '❌ Disabled'}")
                print(f"   User Preferences: {preferences}")
                print()
                continue
                
            elif user_input.lower() == 'preferences':
                preferences = agent.get_preferences()
                if preferences:
                    print(f"\n📋 Current User Preferences:")
                    for key, value in preferences.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"\n📋 No preferences set yet")
                print()
                continue
                
            elif user_input.lower() == 'clear':
                agent.clear_preferences()
                print(f"\n🗑️ All preferences cleared!")
                print()
                continue
                
            elif not user_input:
                print("Please enter a message or 'quit' to exit")
                continue
            
            # Process the input
            print("\n🔄 Processing your request...")
            try:
                response = agent.chat(user_input)
                print(f"\n🤖 Layla: {response}")
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
            
            print("\n" + "-" * 50 + "\n")
    
    except Exception as e:
        print(f"❌ Error initializing agent: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main() 