"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox

Tests for the folder naming service.
"""

import pytest
from backend.services.naming import FolderNamingService


def test_naming_service_initialization():
    """Test that naming service initializes correctly without LLM"""
    service = FolderNamingService()
    assert service.llm_available is False
    assert service.llm_model_path is None


def test_naming_service_with_model_path():
    """Test that naming service handles invalid model path gracefully"""
    service = FolderNamingService(llm_model_path="/nonexistent/model.gguf")
    assert service.llm_available is False  # Should fallback


def test_generate_folder_name_empty_input():
    """Test folder name generation with empty input"""
    service = FolderNamingService()
    name = service.generate_folder_name([])
    assert name == "Uncategorized"


def test_generate_folder_name_space_theme():
    """Test folder name generation for space-related documents"""
    service = FolderNamingService()
    texts = [
        "The planet Mars has a thin atmosphere composed mainly of carbon dioxide.",
        "Jupiter is the largest planet in our solar system with many moons.",
        "The galaxy contains billions of stars and cosmic dust."
    ]
    name = service.generate_folder_name(texts)
    assert name == "Space"  # Should detect space theme


def test_generate_folder_name_cooking_theme():
    """Test folder name generation for cooking-related documents"""
    service = FolderNamingService()
    texts = [
        "This recipe requires flour, eggs, and sugar to make a delicious cake.",
        "The dish is best served with fresh ingredients from the kitchen.",
        "Cook the meal at 350 degrees for 30 minutes for perfect flavor."
    ]
    name = service.generate_folder_name(texts)
    assert name == "Cooking"  # Should detect cooking theme


def test_generate_folder_name_technology_theme():
    """Test folder name generation for technology-related documents"""
    service = FolderNamingService()
    texts = [
        "The algorithm processes data efficiently using advanced programming techniques.",
        "Software development requires understanding of computer systems and APIs.",
        "The function returns a value after executing the code logic."
    ]
    name = service.generate_folder_name(texts)
    assert name == "Technology"  # Should detect technology theme


def test_generate_folder_name_keyword_fallback():
    """Test folder name generation with keyword extraction when no theme detected"""
    service = FolderNamingService()
    texts = [
        "The quick brown fox jumps over the lazy dog multiple times.",
        "Another sentence with the word fox appearing again.",
        "Yet another mention of the fox in this text."
    ]
    name = service.generate_folder_name(texts)
    # Should extract "fox" as most common keyword
    assert "Fox" in name or "Quick" in name or "Brown" in name


def test_generate_batch_names_empty():
    """Test batch name generation with empty input"""
    service = FolderNamingService()
    names = service.generate_batch_names([])
    assert names == []


def test_generate_batch_names_multiple_clusters():
    """Test batch name generation for multiple clusters"""
    service = FolderNamingService()
    clusters = [
        ["The planet Mars orbits the sun.", "Stars shine in the galaxy."],
        ["This recipe uses flour and eggs.", "Cook the dish in the kitchen."],
        ["Programming requires code and algorithms.", "Software development is complex."]
    ]
    names = service.generate_batch_names(clusters)
    assert len(names) == 3
    assert all(isinstance(name, str) for name in names)
    assert all(len(name) > 0 for name in names)


def test_generate_batch_names_with_error():
    """Test batch name generation handles errors gracefully"""
    service = FolderNamingService()
    # Include an empty cluster that might cause issues
    clusters = [
        ["Valid text here"],
        [],  # Empty cluster
        ["More valid text"]
    ]
    names = service.generate_batch_names(clusters)
    assert len(names) == 3
    # Empty cluster should get "Uncategorized" or "Cluster 2"
    assert names[1] in ["Uncategorized", "Cluster 2"]


def test_clean_name():
    """Test name cleaning functionality"""
    service = FolderNamingService()
    
    # Test whitespace removal
    assert service._clean_name("  extra   spaces  ") == "Extra Spaces"
    
    # Test capitalization
    assert service._clean_name("lowercase words") == "Lowercase Words"
    
    # Test empty string
    assert service._clean_name("") == "Uncategorized"
    assert service._clean_name("   ") == "Uncategorized"


def test_enhance_with_themes():
    """Test theme enhancement functionality"""
    service = FolderNamingService()
    
    # Test space theme detection
    space_text = "planet star galaxy universe cosmic astronomy"
    name = service._enhance_with_themes(space_text, "Generic")
    assert name == "Space"
    
    # Test cooking theme detection
    cooking_text = "recipe cook food ingredient dish meal kitchen"
    name = service._enhance_with_themes(cooking_text, "Generic")
    assert name == "Cooking"
    
    # Test no theme detected (below threshold)
    weak_text = "planet hello world"
    name = service._enhance_with_themes(weak_text, "Generic")
    assert name == "Generic"  # Should keep base name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
