@app.post("/api/chat")
async def chat_endpoint(query: str = Body(..., embed=True)):
    """Chatbot endpoint with strong guardrails."""
    try:
        # Check for greetings first
        greeting_response = is_greeting(query)
        if greeting_response:
            return JSONResponse(content={"response": greeting_response})
            
        # Block inappropriate or non-technical queries
        if is_blocked_topic(query):
            return JSONResponse(content={
                "response": "I can only help you with technology-related questions. Please feel free to ask about programming, web development, cloud computing, or other tech topics!"
            })
            
        if not is_tech_query(query):
            return JSONResponse(content={
                "response": "I specialize in technology topics. Could you please ask me something related to programming, development, or other technical subjects?"
            })
        
        # First, try to get context from our portfolio content
        context = await get_portfolio_context(query)
        
        if context:
            # Use retrieved context to generate response
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Answer the following question using the provided context. 
            Focus only on technical information.
            Include code examples where relevant.
            Be friendly but professional.
            Do not mention how you retrieve or process information.
            
            Context: {context}
            Question: {query}
            """
            response = model.generate_content(prompt)
            return JSONResponse(content={
                "response": sanitize_response(format_tech_response(response.text))
            })
            
        # If no context found and it's a technical question, search the web
        web_results = search_web(query)
        if web_results:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Answer the following technical question using the provided information.
            Be precise and include code examples where relevant.
            Be friendly but professional.
            Focus only on technical aspects.
            Do not mention how you retrieve or process information.
            
            Information: {web_results}
            Question: {query}
            """
            response = model.generate_content(prompt)
            return JSONResponse(content={
                "response": sanitize_response(format_tech_response(response.text))
            })
            
        return JSONResponse(content={
            "response": "I apologize, but I couldn't find enough information to answer your technical question accurately. Could you please rephrase or ask another technology-related question?"
        })
        
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "response": "I apologize, but I encountered an error. Please try asking your question again."
            }
        )