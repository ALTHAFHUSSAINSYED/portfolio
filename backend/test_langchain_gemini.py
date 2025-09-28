"""
Test script for LangChain Proxy with Gemini API

This script demonstrates how to use LangChain with Google Gemini models.
"""

import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_gemini_direct():
    """Test direct integration with Google Gemini API"""
    import google.generativeai as genai
    
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error("No API key found for Gemini")
        return
    
    logger.info(f"API key found: {api_key[:6]}...{api_key[-4:]}")
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    # Test a simple generation
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content("Write a Python function to calculate factorial")
    
    logger.info(f"Response from Gemini: {response.text[:100]}...")

def test_langchain_integration():
    """Test LangChain integration with Google Gemini API"""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.chains import LLMChain
    from langchain_core.prompts import PromptTemplate
    
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error("No API key found for Gemini")
        return
    
    # Initialize LangChain with Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.7,
        google_api_key=api_key,
        convert_system_message_to_human=True
    )
    
    # Create a simple prompt template
    template = "Write a {length} paragraph about {topic}"
    prompt = PromptTemplate.from_template(template)
    
    # Create a chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Generate content
    result = chain.run(length="short", topic="artificial intelligence")
    logger.info(f"LangChain + Gemini result: {result[:100]}...")
    
    return result

def test_conversation_chain():
    """Test a conversation chain with memory"""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.chains.conversation.base import ConversationChain
    from langchain.memory import ConversationBufferMemory
    from langchain_core.prompts import PromptTemplate
    
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error("No API key found for Gemini")
        return
    
    # Initialize LangChain with Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.7,
        google_api_key=api_key,
        convert_system_message_to_human=True
    )
    
    # Create a memory
    memory = ConversationBufferMemory()
    
    # Create a conversation prompt
    template = """
    The following is a friendly conversation between a human and an AI assistant.
    The AI assistant is helpful, creative, clever, and very friendly.

    Current conversation:
    {history}
    Human: {input}
    AI: 
    """
    
    prompt = PromptTemplate(
        input_variables=["history", "input"], 
        template=template
    )
    
    # Create conversation chain
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )
    
    # Test conversation
    response1 = conversation.invoke({"input": "Can you help me write code for calculating factorial?"})
    logger.info(f"Response 1: {response1['response'][:100]}...")
    
    return response1

if __name__ == "__main__":
    print("===== Testing Gemini and LangChain Integration =====")
    
    try:
        print("\n🔄 Testing direct Gemini API...")
        test_gemini_direct()
        
        print("\n🔄 Testing LangChain with Gemini...")
        test_langchain_integration()
        
        print("\n🔄 Testing conversation chain...")
        test_conversation_chain()
        
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        print(f"\n❌ Test failed with error: {e}")