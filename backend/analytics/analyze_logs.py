import json
import logging
from pathlib import Path
from collections import defaultdict, Counter
import statistics

# Configuration
ROOT_DIR = Path(__file__).parent.parent.parent
LOG_FILE = ROOT_DIR / 'backend' / 'telemetry.log'

def analyze_logs():
    print(f"🔍 Analyzing logs from: {LOG_FILE}")
    
    if not LOG_FILE.exists():
        print("❌ Log file not found.")
        return

    sessions = set()
    intents = Counter()
    states = Counter()
    latencies = []
    rag_usage = 0
    total_requests = 0
    exits = 0
    
    low_confidence_queries = []

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                # Extract JSON part if mixed with standard logging
                json_part = line.strip()
                if "PortfolioBackend" in line and "{" in line:
                    json_part = line.split(" - ")[-1]
                
                if not json_part.startswith("{"):
                    continue
                    
                data = json.loads(json_part)
                
                # Check if it's a telemetry log
                if "intent_scores" not in data:
                    continue
                    
                total_requests += 1
                sessions.add(data.get("session_id"))
                
                # Aggregation
                final_state = data.get("final_state")
                states[final_state] += 1
                
                if final_state == "EXIT":
                    exits += 1
                    
                if data.get("rag_used"):
                    rag_usage += 1
                    
                # Intent Analysis
                scores = data.get("intent_scores", {})
                # Find winner
                if scores:
                    winner = max(scores, key=scores.get)
                    score = scores[winner]
                    intents[winner] += 1
                    
                    if score < 5 and winner != "conversation":
                        low_confidence_queries.append((data.get("normalized_input"), winner, score))

                # Latency
                lat = data.get("latency_ms", 0)
                if lat > 0:
                    latencies.append(lat)
                    
            except Exception:
                continue

    # --- REPORT GENERATION ---
    print("\n📊 --- CHATBOT INTELLIGENCE REPORT --- 📊")
    print(f"Total Requests: {total_requests}")
    print(f"Unique Sessions: {len(sessions)}")
    
    if total_requests == 0:
        print("No data available.")
        return

    print("\n🔹 State Distribution:")
    for state, count in states.most_common():
        print(f"  - {state}: {count} ({count/total_requests*100:.1f}%)")
        
    print(f"\n🔹 RAG Utilization: {rag_usage/total_requests*100:.1f}%")
    print(f"🔹 Exit Rate: {exits/total_requests*100:.1f}%")
    
    if latencies:
        print(f"\n🔹 Latency (ms):")
        print(f"  - Avg: {statistics.mean(latencies):.0f}ms")
        print(f"  - P95: {statistics.quantiles(latencies, n=20)[-1]:.0f}ms")

    print("\n🔹 Intent Distribution:")
    for intent, count in intents.most_common():
        print(f"  - {intent}: {count}")

    print("\n💡 --- RULE SUGGESTIONS --- 💡")
    if exits > 0:
        print(f"⚠️ High Exit Rate detected ({exits} exits). Check if users are frustrated.")
        
    if low_confidence_queries:
        print("⚠️ Low Confidence Matches (Potential Gaps):")
        for q, i, s in low_confidence_queries[:5]:
            print(f"  - '{q}' mapped to '{i}' with score {s}")
            
    if states["START"] == 0 and total_requests > 10:
        print("ℹ️ 'START' state low. Check session tracking.")

if __name__ == "__main__":
    analyze_logs()
