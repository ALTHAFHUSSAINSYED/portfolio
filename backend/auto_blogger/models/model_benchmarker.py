"""
Model Benchmarker
Tests available models for speed, throughput, and quality to determine the best tier usage.
"""

import os
import time
import json
import logging
import requests
import google.generativeai as genai
from typing import Dict, List, Any
from dotenv import load_dotenv
from .model_config import ALL_MODELS, BENCHMARK_CRITERIA

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ModelBenchmarker")

class ModelBenchmarker:
    def __init__(self):
        # Load environment variables
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))
        
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("CHATBOT_KEY")
        self.gemini_key = os.getenv("GEMINI_BLOG_API_KEY")
        
        if not self.openrouter_key:
            logger.warning("OPENROUTER_API_KEY not found. OpenRouter benchmarks will fail.")
        
        if not self.gemini_key:
             # Try fallback to standard key if dedicated blog key missing
            self.gemini_key = os.getenv("GEMINI_API_KEY")
            logger.info("Using shared GEMINI_API_KEY as fallback for blogs.")
            
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        else:
             logger.warning("No Gemini API key found. Gemini benchmarks will fail.")

    def _test_openrouter(self, model: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Test an OpenRouter model"""
        if not self.openrouter_key:
            return {"error": "No API Key"}

        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://althafportfolio.site",
            "X-Title": "Portfolio Auto-Blogger"
        }
        
        # Use simple prompt for benchmark
        payload = {
            "model": model["model_id"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500  # Limited for benchmark speed
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            duration = time.time() - start_time
            content = data['choices'][0]['message']['content']
            tokens = len(content) / 4  # Approximation
            
            return {
                "success": True,
                "duration": duration,
                "output_length": len(content),
                "estimated_tokens": tokens,
                "tpm": (tokens / duration) * 60 if duration > 0 else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }

    def _test_gemini(self, model: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Test a Gemini model"""
        if not self.gemini_key:
            return {"error": "No API Key"}
            
        start_time = time.time()
        try:
            # Clean model ID for Gemini client (remove 'gemini-' prefix if needed for some versions,
            # but usually it expects 'models/gemini-pro' etc. Let's try direct ID first)
            # The config has IDs like 'gemini-1.5-flash'. genai.GenerativeModel handles this.
            
            gen_model = genai.GenerativeModel(model["model_id"])
            response = gen_model.generate_content(prompt)
            
            duration = time.time() - start_time
            content = response.text
            tokens = len(content) / 4 # Approximation
            
            return {
                "success": True,
                "duration": duration,
                "output_length": len(content),
                "estimated_tokens": tokens,
                "tpm": (tokens / duration) * 60 if duration > 0 else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }

    def run_benchmarks(self) -> Dict[str, Any]:
        """Run standard benchmarks on all models"""
        logger.info("Starting model benchmarks...")
        results = []
        
        test_prompt = "Explain the importance of CI/CD in modern DevOps in exactly 200 words."
        
        for model in ALL_MODELS:
            logger.info(f"Testing {model['name']} ({model['model_id']})...")
            
            if "free" in model["model_id"] or "/" in model["model_id"]:
                result = self._test_openrouter(model, test_prompt)
            else:
                result = self._test_gemini(model, test_prompt)
            
            model_result = {
                "model_name": model["name"],
                "model_id": model["model_id"],
                "tier": model["tier"],
                "benchmark": result
            }
            results.append(model_result)
            
            status = "SUCCESS" if result.get("success") else "FAILED"
            logger.info(f"Result: {status} in {result.get('duration', 0):.2f}s")
            
            # Small delay to avoid rate limits during testing
            time.sleep(2)
            
        return results

    def save_report(self, results: List[Dict[str, Any]], filepath: str = "benchmark_results.json"):
        """Save benchmark results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Benchmark report saved to {filepath}")

if __name__ == "__main__":
    benchmarker = ModelBenchmarker()
    results = benchmarker.run_benchmarks()
    benchmarker.save_report(results)
    
    # Print summary
    print("\n--- BENCHMARK SUMMARY ---")
    for r in results:
        status = "✅" if r["benchmark"].get("success") else "❌"
        duration = r["benchmark"].get("duration", 0)
        tpm = r["benchmark"].get("tpm", 0)
        print(f"{status} {r['model_name']}: {duration:.2f}s | ~{int(tpm)} TPM")
