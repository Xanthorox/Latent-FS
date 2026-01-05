"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

from typing import List, Dict

# Mock documents covering diverse topics
MOCK_DOCUMENTS = [
    # Space (4 documents)
    {
        "text": "The James Webb Space Telescope has revolutionized our understanding of the early universe. Its infrared capabilities allow us to peer through cosmic dust and observe galaxies that formed just a few hundred million years after the Big Bang.",
        "category": "Space"
    },
    {
        "text": "Mars colonization presents unique challenges including radiation exposure, resource scarcity, and psychological effects of isolation. SpaceX's Starship aims to transport humans to Mars within the next decade, establishing the first permanent settlement.",
        "category": "Space"
    },
    {
        "text": "Black holes are regions of spacetime where gravity is so strong that nothing, not even light, can escape. The Event Horizon Telescope captured the first image of a black hole's shadow in 2019, confirming Einstein's predictions.",
        "category": "Space"
    },
    {
        "text": "The International Space Station orbits Earth at approximately 28,000 kilometers per hour, completing 16 orbits per day. Astronauts conduct experiments in microgravity that are impossible on Earth's surface.",
        "category": "Space"
    },
    
    # Cooking (4 documents)
    {
        "text": "Sourdough bread requires a living starter culture of wild yeast and bacteria. The fermentation process develops complex flavors and makes the bread more digestible. Maintaining the starter requires regular feeding with flour and water.",
        "category": "Cooking"
    },
    {
        "text": "The Maillard reaction occurs when proteins and sugars are heated together, creating hundreds of flavor compounds. This chemical process is responsible for the browning and delicious taste of seared steaks, toasted bread, and roasted coffee.",
        "category": "Cooking"
    },
    {
        "text": "Japanese ramen is a complex dish with four main components: broth, noodles, tare (seasoning), and toppings. Traditional tonkotsu broth requires simmering pork bones for 12-18 hours to extract collagen and create a rich, creamy texture.",
        "category": "Cooking"
    },
    {
        "text": "Knife skills are fundamental to efficient cooking. The proper grip involves pinching the blade between thumb and forefinger while wrapping remaining fingers around the handle. A sharp knife is safer than a dull one as it requires less force.",
        "category": "Cooking"
    },
    
    # Coding (4 documents)
    {
        "text": "React hooks revolutionized functional components by allowing state management without classes. useState and useEffect are the most commonly used hooks, enabling developers to build complex applications with cleaner, more maintainable code.",
        "category": "Coding"
    },
    {
        "text": "Docker containers package applications with all dependencies, ensuring consistent behavior across different environments. Containerization has become essential for modern DevOps practices, enabling rapid deployment and scaling.",
        "category": "Coding"
    },
    {
        "text": "Machine learning models require careful feature engineering and hyperparameter tuning. Cross-validation helps prevent overfitting by testing the model on unseen data. Popular frameworks like TensorFlow and PyTorch simplify neural network development.",
        "category": "Coding"
    },
    {
        "text": "Git branching strategies like GitFlow help teams manage code changes efficiently. Feature branches allow developers to work independently, while pull requests enable code review before merging into the main branch.",
        "category": "Coding"
    },
    
    # History (3 documents)
    {
        "text": "The Roman Empire's fall in 476 CE marked the end of ancient history and the beginning of the Middle Ages. Multiple factors contributed including economic troubles, military defeats, and political instability. The Eastern Roman Empire continued as Byzantium for another thousand years.",
        "category": "History"
    },
    {
        "text": "The Industrial Revolution transformed society from agrarian to industrial, beginning in Britain in the late 18th century. Steam power, mechanized textile production, and iron manufacturing created unprecedented economic growth but also harsh working conditions.",
        "category": "History"
    },
    {
        "text": "The Apollo 11 mission in 1969 achieved humanity's first moon landing. Neil Armstrong and Buzz Aldrin spent 21 hours on the lunar surface while Michael Collins orbited above. This achievement demonstrated American technological superiority during the Cold War.",
        "category": "History"
    },
    
    # Finance (3 documents)
    {
        "text": "Compound interest is the eighth wonder of the world according to Einstein. Money invested early grows exponentially over time as interest earns interest. Starting retirement savings in your 20s can result in significantly more wealth than starting in your 30s.",
        "category": "Finance"
    },
    {
        "text": "Diversification reduces portfolio risk by spreading investments across different asset classes, sectors, and geographies. Modern portfolio theory suggests that a mix of stocks, bonds, and alternative investments can optimize returns while minimizing volatility.",
        "category": "Finance"
    },
    {
        "text": "Cryptocurrency operates on blockchain technology, providing decentralized digital currency without central bank control. Bitcoin pioneered this space in 2009, and thousands of alternative coins now exist. Volatility remains a significant concern for mainstream adoption.",
        "category": "Finance"
    },
    
    # Sports (2 documents)
    {
        "text": "Basketball strategy has evolved with analytics showing the efficiency of three-point shots and layups over mid-range jumpers. The Golden State Warriors revolutionized the game with their emphasis on spacing, ball movement, and volume three-point shooting.",
        "category": "Sports"
    },
    {
        "text": "Marathon training requires gradually building endurance over months. Long runs develop aerobic capacity while speed work improves lactate threshold. Proper nutrition, hydration, and recovery are as important as the running itself for peak performance.",
        "category": "Sports"
    }
]


def get_mock_documents() -> List[Dict[str, str]]:
    """
    Get the list of mock documents for testing.
    
    Returns:
        List of dictionaries containing 'text' and 'category' fields
    """
    return MOCK_DOCUMENTS


def populate_database_with_mock_data(db_manager, embedding_service) -> int:
    """
    Populate an empty database with mock documents.
    
    Args:
        db_manager: ChromaDBManager instance
        embedding_service: EmbeddingService instance
        
    Returns:
        Number of documents added
        
    Raises:
        Exception: If database population fails
    """
    try:
        # Extract texts from mock documents
        texts = [doc["text"] for doc in MOCK_DOCUMENTS]
        
        # Generate embeddings in batch for efficiency
        embeddings = embedding_service.embed_batch(texts)
        
        # Add each document to the database
        count = 0
        for i, (doc, embedding) in enumerate(zip(MOCK_DOCUMENTS, embeddings)):
            doc_id = f"mock_doc_{i}"
            metadata = {
                "category": doc["category"],
                "source": "mock_data"
            }
            
            db_manager.add_document(
                doc_id=doc_id,
                text=doc["text"],
                embedding=embedding,
                metadata=metadata
            )
            count += 1
        
        return count
        
    except Exception as e:
        raise Exception(f"Failed to populate database with mock data: {str(e)}")
