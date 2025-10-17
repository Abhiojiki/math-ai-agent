"""
Download MATH dataset from HuggingFace - ALL SAMPLES for better accuracy.
This downloads the full dataset (~12K problems) for production-ready knowledge base.
"""

import json
from datasets import load_dataset
from pathlib import Path
import os

def download_math_dataset():
    """Download complete MATH dataset from HuggingFace."""
    
    print("📥 Downloading COMPLETE MATH dataset from HuggingFace...")
    print("⏳ This will take 2-3 minutes (downloading ~12,500 problems)...")
    
    # Get the correct path (we're in scripts folder)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    data_dir = project_root / "data"
    output_path = data_dir / "math_kb.json"
    
    # Create data directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📂 Data directory: {data_dir}")
    
    try:
        # Load FULL dataset from HuggingFace
        dataset = load_dataset(
            "qwedsacf/competition_math",
            split="train",
            trust_remote_code=True
        )
        
        print(f"✅ Dataset loaded. Total samples: {len(dataset)}")
        
        # Convert all samples to our format
        all_data = []
        
        for item in dataset:
            all_data.append({
                'problem': item['problem'],
                'solution': item['solution'],
                'level': item['level'],
                'type': item['type']
            })
        
        print(f"✅ Processed {len(all_data)} samples (ALL levels)")
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dataset saved to {output_path}")
        print(f"📊 Dataset statistics:\n")
        
        # Show distribution
        level_counts = {}
        type_counts = {}
        
        for item in all_data:
            level = item['level']
            topic = item['type']
            level_counts[level] = level_counts.get(level, 0) + 1
            type_counts[topic] = type_counts.get(topic, 0) + 1
        
        print("By Difficulty Level:")
        for level, count in sorted(level_counts.items()):
            print(f"  {level}: {count}")
        
        print("\nBy Math Topic:")
        for topic, count in sorted(type_counts.items()):
            print(f"  {topic}: {count}")
        
        return len(all_data)
    
    except Exception as e:
        print(f"❌ ERROR downloading dataset: {e}")
        raise

if __name__ == "__main__":
    try:
        total = download_math_dataset()
        print(f"\n🎉 SUCCESS! Downloaded {total} math problems")
        print("✅ Next step: Run setup_vector_store.py")
    except Exception as e:
        print(f"❌ FAILED: {e}")
