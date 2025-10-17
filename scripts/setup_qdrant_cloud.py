"""
Upload MATH dataset to Qdrant Cloud - FIXED VERSION
Works with qdrant-client 1.12.0+ (uses numeric timeout instead of httpx.Timeout)
"""

import json
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os
from dotenv import load_dotenv
import time
import random

# Load environment variables
env_path = Path(__file__).parent.parent 

env_path = env_path / "backend" / "app" / ".env"
load_dotenv(env_path)

def setup_qdrant_cloud():
    """Upload complete dataset to Qdrant Cloud with proper error handling."""
    
    print("🚀 Setting up Qdrant Cloud vector database...")
    
    # Get paths
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    data_path = project_root / "data" / "math_kb.json"
    
    # Load environment variables
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "math_knowledge_base")
    
    if not qdrant_url or not qdrant_api_key:
        raise ValueError(
            "❌ Please set QDRANT_URL and QDRANT_API_KEY in backend/.env file\n"
            "Get these from https://cloud.qdrant.io/"
        )
    
    print(f"📂 Loading dataset from: {data_path}")
    
    # Load dataset
    with open(data_path, 'r', encoding='utf-8') as f:
        math_data = json.load(f)
    
    print(f"✅ Loaded {len(math_data)} problems")
    
    # Initialize Qdrant client with NUMERIC timeout (180 seconds)
    print(f"🔗 Connecting to Qdrant Cloud (timeout: 180s)...")
    
    # FIX: Use numeric timeout value instead of httpx.Timeout object
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        timeout=180  # 180 seconds total timeout (numeric value)
    )
    
    print("✅ Connected to Qdrant Cloud")
    
    # Initialize embedding model
    print("🔧 Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding_dim = 384
    
    print("✅ Embedding model ready")
    
    # Create/recreate collection
    print(f"📦 Setting up collection: {collection_name}")
    
    try:
        # Delete collection if exists
        client.delete_collection(collection_name=collection_name)
        print(f"  ✓ Deleted existing collection")
        time.sleep(2)
    except:
        print(f"  ✓ No existing collection to delete")
    
    # Create collection with optimized settings
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=embedding_dim,
            distance=Distance.COSINE
        )
    )
    
    print(f"✅ Collection '{collection_name}' created")
    
    # Batch upload configuration
    print("\n📤 Starting batch upload...")
    print("⚙️  Configuration:")
    print("   • Batch size: 100 points")
    print("   • Rate limit: 0.5s between batches")
    print("   • Retry attempts: 3 per batch")
    print("   • Estimated time: 15-20 minutes\n")
    
    BATCH_SIZE = 100  # Conservative batch size for stability
    SLEEP_BETWEEN_BATCHES = 0.5  # 500ms delay
    MAX_RETRIES = 3
    
    total_uploaded = 0
    failed_batches = []
    
    # Process in batches with progress bar
    num_batches = (len(math_data) + BATCH_SIZE - 1) // BATCH_SIZE
    
    with tqdm(total=len(math_data), desc="Uploading", unit="problems") as pbar:
        for batch_start in range(0, len(math_data), BATCH_SIZE):
            batch_data = math_data[batch_start:batch_start + BATCH_SIZE]
            batch_num = batch_start // BATCH_SIZE + 1
            
            # Prepare batch embeddings and points
            points = []
            
            for idx, item in enumerate(batch_data):
                global_idx = batch_start + idx
                
                # Create text for embedding
                text_content = f"Problem: {item['problem']}\n\nSolution: {item['solution']}"
                
                # Generate embedding
                embedding = model.encode(text_content).tolist()
                
                # Create point
                point = PointStruct(
                    id=global_idx,
                    vector=embedding,
                    payload={
                        'problem': item['problem'],
                        'solution': item['solution'],
                        'level': item['level'],
                        'type': item['type'],
                        'text': text_content
                    }
                )
                points.append(point)
            
            # Upload with retry logic
            upload_success = False
            
            for attempt in range(MAX_RETRIES):
                try:
                    client.upsert(
                        collection_name=collection_name,
                        points=points
                    )
                    total_uploaded += len(points)
                    upload_success = True
                    pbar.update(len(points))
                    break
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    if "timeout" in error_msg or "timed out" in error_msg:
                        # Exponential backoff
                        sleep_time = min(30, (2 ** attempt) + random.uniform(0, 1))
                        pbar.write(f"⚠️  Batch {batch_num}/{num_batches} timeout, "
                                  f"retry {attempt + 1}/{MAX_RETRIES} in {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                    else:
                        pbar.write(f"❌ Batch {batch_num} error: {e}")
                        raise
            
            if not upload_success:
                failed_batches.append(batch_start)
                pbar.write(f"❌ Batch {batch_num} failed after {MAX_RETRIES} retries")
            
            # Rate limiting
            if upload_success and batch_start + BATCH_SIZE < len(math_data):
                time.sleep(SLEEP_BETWEEN_BATCHES)
    
    print(f"\n✅ Upload complete! Uploaded: {total_uploaded}/{len(math_data)} problems")
    
    # Report failures
    if failed_batches:
        print(f"\n⚠️  {len(failed_batches)} batches failed:")
        print(f"   Failed indices: {failed_batches}")
    
    # Wait for indexing
    print("\n⏳ Waiting for indexing (15 seconds)...")
    time.sleep(15)
    
    # Get collection info
    try:
        collection_info = client.get_collection(collection_name=collection_name)
        print(f"\n📊 Collection Statistics:")
        print(f"   Total vectors: {collection_info.points_count}")
        print(f"   Vector dimension: {embedding_dim}")
        print(f"   Distance metric: COSINE")
    except Exception as e:
        print(f"⚠️  Could not retrieve stats: {e}")
    
    # Test search functionality
    print("\n🧪 Testing search functionality...\n")
    
    test_queries = [
        "What is the quadratic formula?",
        "How to find derivative of x squared?",
        "Explain Pythagorean theorem"
    ]
    
    for test_query in test_queries:
        try:
            query_vector = model.encode(test_query).tolist()
            
            results = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=2
            )
            
            print(f"Query: '{test_query}'")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  ✓ Result {i} (Score: {result.score:.3f})")
                    print(f"    Level: {result.payload['level']}, Topic: {result.payload['type']}")
                    print(f"    Problem: {result.payload['problem'][:80]}...")
            else:
                print("  ⚠️  No results found")
            print()
                
        except Exception as e:
            print(f"  ❌ Search failed: {e}\n")
    
    print("✅ Qdrant Cloud setup complete!")
    return client

if __name__ == "__main__":
    try:
        print("="*70)
        print("           QDRANT CLOUD UPLOAD - FIXED VERSION")
        print("="*70)
        print("\nFeatures:")
        print("  ✓ Numeric timeout (180 seconds)")
        print("  ✓ Batch size: 100 points")
        print("  ✓ Rate limiting: 500ms between batches")
        print("  ✓ Retry logic: 3 attempts with exponential backoff")
        print("  ✓ Progress tracking with tqdm")
        print("\nEstimated time: 15-20 minutes for 12,500 problems")
        print("="*70 + "\n")
        
        client = setup_qdrant_cloud()
        
        print("\n" + "="*70)
        print("           🎉 SUCCESS! Qdrant Cloud Ready")
        print("="*70)
        print("\n✅ Next steps:")
        print("   1. Test with: python test_agent.py")
        print("   2. Create remaining backend files (guardrails, web_search)")
        print("   3. Build FastAPI endpoints\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Upload interrupted by user")
        print("Note: Partial data uploaded. Safe to re-run.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Troubleshooting:")
        print("   1. Verify QDRANT_URL format: https://xxx.cloud.qdrant.io")
        print("   2. Check QDRANT_API_KEY is correct")
        print("   3. Ensure cluster is running at cloud.qdrant.io")
        print("   4. Check internet connection stability")
        print("   5. Try reducing BATCH_SIZE to 50 if still fails\n")
