import sys
sys.path.append('backend')

from services.database import ChromaDBManager

print("=== CHECKING DATABASE ===\n")

db = ChromaDBManager()

# Get all documents
try:
    result = db.collection.get(include=['metadatas'])
    doc_count = len(result['ids'])
    print(f"[OK] Total Documents: {doc_count}")
    
    # Check cluster distribution
    cluster_counts = {}
    for metadata in result['metadatas']:
        cluster_id = metadata.get('cluster_id', 'NONE')
        cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1
    
    print(f"\n=== CLUSTER DISTRIBUTION ===")
    for cluster_id, count in sorted(cluster_counts.items()):
        print(f"  {cluster_id}: {count} documents")
    
    # Check for documents without cluster_id
    no_cluster = [doc_id for doc_id, meta in zip(result['ids'], result['metadatas']) if not meta.get('cluster_id')]
    if no_cluster:
        print(f"\n[WARNING] {len(no_cluster)} documents without cluster_id!")
        print(f"  IDs: {no_cluster[:5]}")
    else:
        print(f"\n[OK] All documents have cluster_id")
    
    # Check for duplicate IDs
    if len(result['ids']) != len(set(result['ids'])):
        print(f"\n[WARNING] Duplicate document IDs found!")
    else:
        print(f"[OK] No duplicate document IDs")
    
    print(f"\n[INFO] Database needs vacuuming - run: chromadb utils vacuum")
        
except Exception as e:
    print(f"[ERROR] Error checking database: {e}")
    import traceback
    traceback.print_exc()
