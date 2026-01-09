"""
Google Gemini API client for Guardian
Handles communication with Gemini AI model via Antigravity Auth
"""

import time
import asyncio
from typing import Optional, Dict, Any, List

# Use Antigravity Service instead of LangChain
from antigravity_auth import AntigravityService
from utils.logger import get_logger


class GeminiClient:
    """Google Gemini API client wrapper using Antigravity Auth"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(config)
        
        # Initialize Gemini model via Antigravity
        ai_config = config.get("ai", {})
        self.model_name = ai_config.get("model", "gemini-3-pro")
        
        # Rate limiting: requests per minute
        self.rate_limit = ai_config.get("rate_limit", 60)  # Default 60 RPM
        self._min_request_interval = 60.0 / self.rate_limit if self.rate_limit > 0 else 0
        self._last_request_time = 0.0
        
        try:
            # Initialize Antigravity Service
            self.service = AntigravityService(model=self.model_name)
            self.logger.info(f"Initialized Antigravity model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Antigravity client: {e}")
            raise
    
    async def _apply_rate_limit(self):
        """Apply rate limiting between API calls"""
        if self._min_request_interval > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                wait_time = self._min_request_interval - elapsed
                self.logger.debug(f"Rate limiting: waiting {wait_time:.2f}s before next request")
                await asyncio.sleep(wait_time)
        self._last_request_time = time.time()
    
    def _apply_rate_limit_sync(self):
        """Synchronous rate limiting"""
        if self._min_request_interval > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                wait_time = self._min_request_interval - elapsed
                self.logger.debug(f"Rate limiting: waiting {wait_time:.2f}s before next request")
                time.sleep(wait_time)
        self._last_request_time = time.time()
    
    def _format_context(self, context: Optional[List[Any]]) -> List[Dict[str, Any]]:
        """Format context messages for Antigravity (Gemini format)."""
        formatted_messages = []
        if context:
            for msg in context:
                # Handle LangChain message objects if they are passed
                if hasattr(msg, "content") and hasattr(msg, "type"):
                    role = "user" if msg.type == "human" else "model"
                    formatted_messages.append({
                        "role": role,
                        "parts": [{"text": msg.content}]
                    })
                # Handle raw dicts
                elif isinstance(msg, dict):
                    formatted_messages.append(msg)
        return formatted_messages

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """
        Generate a response from Gemini using Antigravity
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for instructions
            context: Optional conversation history
        
        Returns:
            Generated response text
        """
        try:
            # Apply rate limiting
            await self._apply_rate_limit()
            
            # Use Antigravity Service
            # Note: AntigravityService handles message formatting internally, 
            # so we just pass prompt and system_prompt directly.
            # If context is provided, we might need a way to pass it.
            # Currently AntigravityService.generate is simple.
            # Let's use the underlying client or update service if needed.
            # For now, let's assume simple prompt/system_prompt usage.
            
            # Create a combined prompt if context exists (simplified for now)
            # A better approach would be to update AntigravityService to accept history
            full_prompt = prompt
            if context:
                # Simple append for context if not fully supported by service wrapper yet
                # This is a temporary shim until service supports full history
                formatted_history = "\n".join([
                    f"{msg.get('role', 'user')}: {msg.get('parts', [{'text': ''}])[0].get('text', '')}" 
                    if isinstance(msg, dict) else str(msg)
                    for msg in self._format_context(context)
                ])
                if formatted_history:
                    full_prompt = f"Previous conversation:\n{formatted_history}\n\nCurrent user request:\n{prompt}"

            response = await self.service.generate(
                prompt=full_prompt,
                system_prompt=system_prompt
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Antigravity API error: {e}")
            raise
    
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """Synchronous version of generate"""
        try:
            # Apply rate limiting
            self._apply_rate_limit_sync()
            
            full_prompt = prompt
            if context:
                formatted_history = "\n".join([
                    f"{msg.get('role', 'user')}: {msg.get('parts', [{'text': ''}])[0].get('text', '')}" 
                    if isinstance(msg, dict) else str(msg)
                    for msg in self._format_context(context)
                ])
                if formatted_history:
                    full_prompt = f"Previous conversation:\n{formatted_history}\n\nCurrent user request:\n{prompt}"
            
            response = self.service.generate_sync(
                prompt=full_prompt,
                system_prompt=system_prompt
            )
            return response
            
        except Exception as e:
            self.logger.error(f"Antigravity API error: {e}")
            raise
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        system_prompt: str,
        context: Optional[list] = None
    ) -> Dict[str, str]:
        """
        Generate response with explicit reasoning
        
        Returns:
            Dict with 'reasoning' and 'response' keys
        """
        # Enhanced prompt to extract reasoning
        enhanced_prompt = f"""{prompt}

Please structure your response as:
1. REASONING: Explain your thought process and decision-making
2. RESPONSE: Provide your final answer or recommendation
"""
        
        response = await self.generate(enhanced_prompt, system_prompt, context)
        
        # Parse reasoning and response
        parts = {"reasoning": "", "response": ""}
        
        if "REASONING:" in response and "RESPONSE:" in response:
            try:
                # Find indices to slice the string safely
                reasoning_idx = response.find("REASONING:")
                response_idx = response.find("RESPONSE:")
                
                if reasoning_idx != -1 and response_idx != -1:
                    reasoning_content = response[reasoning_idx + len("REASONING:"):response_idx].strip()
                    response_content = response[response_idx + len("RESPONSE:"):].strip()
                    
                    parts["reasoning"] = reasoning_content
                    parts["response"] = response_content
                else:
                     parts["response"] = response
                     parts["reasoning"] = "Parsing failed, check format."
            except Exception:
                parts["response"] = response
                parts["reasoning"] = "Error parsing response structure"
        else:
            # If not properly formatted, put everything in response
            parts["response"] = response
            parts["reasoning"] = "No explicit reasoning provided"
        
        return parts
