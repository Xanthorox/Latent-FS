"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Performance benchmarking tests
"""

import sys
from pathlib import Path
import time
import statistics

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.embedding import EmbeddingService
from backend.services.database import ChromaDBManager
from backend.services.clustering import ClusterEngine
from backend.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def benchmark_embedding_speed():
    """
    Benchmark embedding generation speed (GPU vs CPU)
    Validates: Requirements 1.1
    """
    print("\n" + "="*70)
    print("BENCHMARK 1: Embedding Generation Speed")
    print("="*70 + "\n")
    
    # Initialize embedding service
    embedding_service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    
    print(f"Device: {embedding_service.device}")
    print(f"Model: {settings.EMBEDDING_MODEL}\n")
    
    # Test single embedding
    print("Test 1.1: Single text embedding...")
    test_text = "Machine learning is a subset of artificial intelligence that enables computers to learn from data."
    
    times = []
    for i in range(10):
        start = time.time()
        embedding = embedding_service.embed_text(test_text)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"   ✓ Average time: {avg_time*1000:.2f}ms")
    print(f"   ✓ Std deviation: {std_dev*1000:.2f}ms")
    print(f"   ✓ Min time: {min(times)*1000:.2f}ms")
    print(f"   ✓ Max time: {max(times)*1000:.2f}ms")
    print(f"   ✓ Embedding dimension: {len(embedding)}\n")
    
    # Test batch embedding
    print("Test 1.2: Batch embedding (10 texts)...")
    test_texts = [
        f"This is test document number {i} with some sample content about various topics."
        for i in range(10)
    ]
    
    times = []
    for i in range(5):
        start = time.time()
        embeddings = embedding_service.embed_batch(test_texts)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    per_doc = avg_time / len(test_texts)
    
    print(f"   ✓ Average batch time: {avg_time*1000:.2f}ms")
    print(f"   ✓ Time per document: {per_doc*1000:.2f}ms")
    print(f"   ✓ Std deviation: {std_dev*1000:.2f}ms")
    print(f"   ✓ Throughput: {len(test_texts)/avg_time:.2f} docs/sec\n")
    
    # Test larger batch
    print("Test 1.3: Large batch embedding (100 texts)...")
    large_texts = [
        f"Document {i}: This is a longer test document with more content to simulate real-world usage patterns."
        for i in range(100)
    ]
    
    start = time.time()
    large_embeddings = embedding_service.embed_batch(large_texts)
    elapsed = time.time() - start
    per_doc = elapsed / len(large_texts)
    
    print(f"   ✓ Total time: {elapsed:.2f}s")
    print(f"   ✓ Time per document: {per_doc*1000:.2f}ms")
    print(f"   ✓ Throughput: {len(large_texts)/elapsed:.2f} docs/sec")
    
    print("\n✅ BENCHMARK 1 COMPLETE\n")


def benchmark_clustering_performance():
    """
    Benchmark clustering with varying document counts
    Validates: Requirements 2.2
    """
    print("\n" + "="*70)
    print("BENCHMARK 2: Clustering Performance")
    print("="*70 + "\n")
    
    # Initialize services
    embedding_service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    db = ChromaDBManager(persist_directory="./data/chroma_perf_test")
    db.reset_database()
    
    # Test with different document counts
    test_sizes = [10, 50, 100, 500]
    
    for size in test_sizes:
        print(f"Test 2.{test_sizes.index(size)+1}: Clustering {size} documents...")
        
        # Generate documents
        texts = [
            f"Document {i}: Sample content about topic {i % 10} with various keywords and information."
            for i in range(size)
        ]
        
        # Embed and store
        setup_start = time.time()
        for i, text in enumerate(texts):
            embedding = embedding_service.embed_text(text)
            db.add_document(doc_id=f"doc_{i}", text=text, embedding=embedding)
        setup_time = time.time() - setup_start
        
        # Benchmark clustering
        all_docs = db.get_all_documents()
        
        # Determine appropriate cluster count
        n_clusters = min(5, max(2, size // 20))
        cluster_engine = ClusterEngine(n_clusters=n_clusters)
        
        times = []
        for _ in range(3):
            start = time.time()
            clusters_dict = cluster_engine.cluster_documents(all_docs)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        print(f"   ✓ Setup time (embedding + storage): {setup_time:.2f}s")
        print(f"   ✓ Clustering time: {avg_time*1000:.2f}ms")
        print(f"   ✓ Std deviation: {std_dev*1000:.2f}ms")
        print(f"   ✓ Clusters created: {len(clusters_dict)}")
        print(f"   ✓ Time per document: {(avg_time/size)*1000:.2f}ms\n")
        
        # Clean for next test
        db.reset_database()
    
    print("✅ BENCHMARK 2 COMPLETE\n")


def benchmark_database_operations():
    """
    Benchmark database read/write performance
    """
    print("\n" + "="*70)
    print("BENCHMARK 3: Database Operations")
    print("="*70 + "\n")
    
    # Initialize services
    embedding_service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    db = ChromaDBManager(persist_directory="./data/chroma_perf_test")
    db.reset_database()
    
    # Test write performance
    print("Test 3.1: Write performance (100 documents)...")
    texts = [f"Test document {i} with sample content" for i in range(100)]
    embeddings = embedding_service.embed_batch(texts)
    
    start = time.time()
    for i, (text, embedding) in enumerate(zip(texts, embeddings)):
        db.add_document(doc_id=f"doc_{i}", text=text, embedding=embedding)
    write_time = time.time() - start
    
    print(f"   ✓ Total write time: {write_time:.2f}s")
    print(f"   ✓ Time per document: {(write_time/len(texts))*1000:.2f}ms")
    print(f"   ✓ Write throughput: {len(texts)/write_time:.2f} docs/sec\n")
    
    # Test read performance
    print("Test 3.2: Read performance (single document)...")
    times = []
    for _ in range(100):
        start = time.time()
        doc = db.get_document("doc_50")
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    print(f"   ✓ Average read time: {avg_time*1000:.2f}ms")
    print(f"   ✓ Min: {min(times)*1000:.2f}ms, Max: {max(times)*1000:.2f}ms\n")
    
    # Test bulk read performance
    print("Test 3.3: Bulk read performance (all documents)...")
    times = []
    for _ in range(10):
        start = time.time()
        all_docs = db.get_all_documents()
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    print(f"   ✓ Average bulk read time: {avg_time*1000:.2f}ms")
    print(f"   ✓ Documents retrieved: {len(all_docs)}")
    print(f"   ✓ Time per document: {(avg_time/len(all_docs))*1000:.2f}ms\n")
    
    # Test update performance
    print("Test 3.4: Update performance (embedding updates)...")
    new_embedding = embedding_service.embed_text("Updated content")
    
    times = []
    for i in range(10):
        start = time.time()
        db.update_embedding(f"doc_{i}", new_embedding)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    print(f"   ✓ Average update time: {avg_time*1000:.2f}ms")
    print(f"   ✓ Update throughput: {1/avg_time:.2f} updates/sec\n")
    
    # Cleanup
    db.reset_database()
    print("✅ BENCHMARK 3 COMPLETE\n")


def benchmark_reembedding_operations():
    """
    Benchmark re-embedding operation latency
    """
    print("\n" + "="*70)
    print("BENCHMARK 4: Re-Embedding Operations")
    print("="*70 + "\n")
    
    from backend.services.reembedding import ReEmbeddingEngine
    
    # Initialize services
    embedding_service = EmbeddingService(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.DEVICE
    )
    reembed_engine = ReEmbeddingEngine(alpha=0.3)
    
    # Generate test embeddings
    print("Test 4.1: Re-embedding calculation speed...")
    test_text = "Sample document for re-embedding test"
    current_embedding = embedding_service.embed_text(test_text)
    target_text = "Target cluster representative document"
    target_centroid = embedding_service.embed_text(target_text)
    
    times = []
    for _ in range(1000):
        start = time.time()
        new_embedding = reembed_engine.nudge_embedding(current_embedding, target_centroid)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times)
    
    print(f"   ✓ Average re-embedding time: {avg_time*1000:.4f}ms")
    print(f"   ✓ Std deviation: {std_dev*1000:.4f}ms")
    print(f"   ✓ Min: {min(times)*1000:.4f}ms, Max: {max(times)*1000:.4f}ms")
    print(f"   ✓ Throughput: {1/avg_time:.2f} operations/sec\n")
    
    # Test similarity calculation
    print("Test 4.2: Similarity calculation speed...")
    times = []
    for _ in range(1000):
        start = time.time()
        similarity = reembed_engine.calculate_similarity(current_embedding, target_centroid)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    print(f"   ✓ Average similarity calc time: {avg_time*1000:.4f}ms")
    print(f"   ✓ Throughput: {1/avg_time:.2f} calculations/sec\n")
    
    print("✅ BENCHMARK 4 COMPLETE\n")


def run_all_performance_tests():
    """Run all performance benchmarks"""
    print("\n" + "="*70)
    print("RUNNING PERFORMANCE BENCHMARKS")
    print("="*70)
    
    start_time = time.time()
    
    try:
        benchmark_embedding_speed()
        benchmark_clustering_performance()
        benchmark_database_operations()
        benchmark_reembedding_operations()
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"✅ ALL PERFORMANCE BENCHMARKS COMPLETE ({elapsed:.2f}s)")
        print("="*70 + "\n")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ BENCHMARK FAILED: {e}")
        print(f"Time elapsed: {elapsed:.2f}s\n")
        raise


if __name__ == "__main__":
    run_all_performance_tests()
