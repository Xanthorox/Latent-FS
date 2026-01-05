"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Demonstration of the folder naming service.
"""

from backend.services.naming import FolderNamingService


def main():
    """Demonstrate the folder naming service with various document types"""
    
    print("=" * 70)
    print("Latent-FS Folder Naming Service Demo")
    print("=" * 70)
    
    # Initialize the naming service
    naming_service = FolderNamingService()
    
    # Test cases with different themes
    test_cases = [
        {
            "name": "Space Documents",
            "texts": [
                "The planet Mars has a thin atmosphere composed mainly of carbon dioxide.",
                "Jupiter is the largest planet in our solar system with many moons.",
                "The galaxy contains billions of stars and cosmic dust."
            ]
        },
        {
            "name": "Cooking Documents",
            "texts": [
                "This recipe requires flour, eggs, and sugar to make a delicious cake.",
                "The dish is best served with fresh ingredients from the kitchen.",
                "Cook the meal at 350 degrees for 30 minutes for perfect flavor."
            ]
        },
        {
            "name": "Technology Documents",
            "texts": [
                "The algorithm processes data efficiently using advanced programming techniques.",
                "Software development requires understanding of computer systems and APIs.",
                "The function returns a value after executing the code logic."
            ]
        },
        {
            "name": "Finance Documents",
            "texts": [
                "Stock market trading requires careful analysis of financial indicators.",
                "Investment portfolios should be diversified to minimize risk.",
                "The economy shows signs of growth with increasing business revenue."
            ]
        },
        {
            "name": "History Documents",
            "texts": [
                "Ancient civilizations built impressive monuments that still stand today.",
                "The war lasted for several years and changed the course of history.",
                "Historical records from the medieval period reveal fascinating insights."
            ]
        }
    ]
    
    print("\nGenerating folder names for different document clusters:\n")
    
    for test_case in test_cases:
        print(f"Input: {test_case['name']}")
        print(f"Sample text: {test_case['texts'][0][:60]}...")
        
        # Generate folder name
        folder_name = naming_service.generate_folder_name(test_case['texts'])
        
        print(f"Generated folder name: '{folder_name}'")
        print("-" * 70)
    
    # Test batch naming
    print("\nBatch naming demonstration:\n")
    all_texts = [test_case['texts'] for test_case in test_cases]
    batch_names = naming_service.generate_batch_names(all_texts)
    
    print("Batch-generated names:")
    for i, name in enumerate(batch_names):
        print(f"  Cluster {i + 1}: '{name}'")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
