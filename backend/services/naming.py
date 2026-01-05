"""
Latent-FS - The Vector File System
Author: Gary Dev of Xanthorox
Copyright © 2026 Xanthorox
"""

import logging
from typing import List, Optional
from collections import Counter
import re

logger = logging.getLogger(__name__)


class FolderNamingService:
    """
    Service for generating semantic folder names for document clusters.
    
    This service uses a local LLM to generate meaningful names based on
    representative documents from each cluster. If the LLM is unavailable
    or fails, it falls back to generating descriptive names based on
    keyword extraction from the documents.
    """
    
    def __init__(self, llm_model_path: Optional[str] = None):
        """
        Initialize the folder naming service with optional LLM model.
        
        Args:
            llm_model_path: Path to the local LLM model file (e.g., .gguf file)
                          If None or model loading fails, uses fallback naming
        """
        self.llm_model_path = llm_model_path
        self.llm_available = False
        
        if llm_model_path:
            try:
                self._initialize_llm(llm_model_path)
            except Exception as e:
                logger.warning(
                    f"Failed to initialize LLM from '{llm_model_path}': {e}. "
                    "Using fallback naming strategy."
                )
        else:
            logger.info("No LLM model path provided. Using fallback naming strategy.")
    
    def _initialize_llm(self, model_path: str):
        """
        Initialize the local LLM for name generation.
        
        This method attempts to load a local LLM using llama.cpp or similar.
        Currently implements a placeholder that can be extended with actual
        LLM integration.
        
        Args:
            model_path: Path to the LLM model file
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        # Placeholder for LLM initialization
        # In a full implementation, this would use llama-cpp-python or similar:
        #
        # from llama_cpp import Llama
        # self.llm = Llama(
        #     model_path=model_path,
        #     n_ctx=512,
        #     n_threads=4,
        #     n_gpu_layers=35  # Use GPU if available
        # )
        # self.llm_available = True
        
        logger.info(f"LLM initialization placeholder for model: {model_path}")
        logger.info("To enable LLM naming, install llama-cpp-python and provide a valid model")
        self.llm_available = False
    
    def generate_folder_name(self, representative_texts: List[str]) -> str:
        """
        Generate a semantic folder name from representative documents.
        
        This method analyzes the representative documents from a cluster
        and generates a concise, meaningful name (2-3 words) that captures
        the semantic theme of the cluster.
        
        Args:
            representative_texts: List of text strings from representative documents
        
        Returns:
            A semantic folder name (2-3 words)
        """
        if not representative_texts:
            logger.warning("No representative texts provided, using default name")
            return "Uncategorized"
        
        # Try LLM generation if available
        if self.llm_available:
            try:
                return self._generate_with_llm(representative_texts)
            except Exception as e:
                logger.warning(f"LLM generation failed: {e}. Using fallback.")
        
        # Fallback to keyword-based naming
        return self._generate_fallback_name(representative_texts)
    
    def generate_batch_names(self, clusters: List[List[str]]) -> List[str]:
        """
        Generate names for multiple clusters efficiently.
        
        This method processes multiple clusters in batch, generating a
        semantic name for each cluster based on its representative documents.
        
        Args:
            clusters: List of clusters, where each cluster is a list of
                     representative document texts
        
        Returns:
            List of folder names, one for each cluster
        """
        if not clusters:
            return []
        
        logger.info(f"Generating names for {len(clusters)} clusters")
        
        names = []
        for i, cluster_texts in enumerate(clusters):
            try:
                name = self.generate_folder_name(cluster_texts)
                names.append(name)
                logger.debug(f"Generated name for cluster {i}: '{name}'")
            except Exception as e:
                logger.error(f"Failed to generate name for cluster {i}: {e}")
                names.append(f"Cluster {i + 1}")
        
        return names
    
    def _generate_with_llm(self, representative_texts: List[str]) -> str:
        """
        Generate folder name using the local LLM.
        
        This method constructs a prompt and queries the LLM to generate
        a semantic folder name based on the representative documents.
        
        Args:
            representative_texts: List of representative document texts
        
        Returns:
            LLM-generated folder name
        
        Raises:
            Exception: If LLM generation fails
        """
        # Construct prompt for LLM
        combined_text = "\n\n".join(representative_texts[:3])  # Use top 3 docs
        prompt = f"""Based on these documents, suggest a concise 2-3 word category name:

{combined_text}

Category name:"""
        
        # Placeholder for actual LLM call
        # In a full implementation:
        #
        # response = self.llm(
        #     prompt,
        #     max_tokens=20,
        #     temperature=0.7,
        #     stop=["\n", ".", ","]
        # )
        # name = response['choices'][0]['text'].strip()
        # return self._clean_name(name)
        
        raise Exception("LLM not available")
    
    def _generate_fallback_name(self, representative_texts: List[str]) -> str:
        """
        Generate folder name using keyword extraction fallback.
        
        This method extracts important keywords from the representative
        documents and constructs a meaningful folder name without using
        an LLM. It uses simple NLP techniques like word frequency and
        filtering.
        
        Args:
            representative_texts: List of representative document texts
        
        Returns:
            Keyword-based folder name
        """
        # Combine all texts
        combined_text = " ".join(representative_texts).lower()
        
        # Extract words (alphanumeric only)
        words = re.findall(r'\b[a-z]{3,}\b', combined_text)
        
        # Common stop words to filter out
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him',
            'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way',
            'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too',
            'use', 'with', 'this', 'that', 'from', 'have', 'they', 'will',
            'what', 'been', 'more', 'when', 'your', 'than', 'into', 'very',
            'some', 'time', 'about', 'after', 'could', 'their', 'would',
            'there', 'these', 'which', 'other', 'being', 'where', 'through'
        }
        
        # Filter stop words and count frequency
        filtered_words = [w for w in words if w not in stop_words]
        
        if not filtered_words:
            return "Documents"
        
        # Get most common words
        word_counts = Counter(filtered_words)
        most_common = word_counts.most_common(3)
        
        # Build name from top keywords
        if len(most_common) >= 2:
            # Use top 2 keywords
            name = f"{most_common[0][0].capitalize()} {most_common[1][0].capitalize()}"
        elif len(most_common) == 1:
            name = most_common[0][0].capitalize()
        else:
            name = "Documents"
        
        # Detect common themes
        name = self._enhance_with_themes(combined_text, name)
        
        return name
    
    def _enhance_with_themes(self, text: str, base_name: str) -> str:
        """
        Enhance the base name by detecting common themes in the text.
        
        This method looks for domain-specific keywords and adjusts the
        folder name to be more descriptive.
        
        Args:
            text: Combined text from representative documents
            base_name: Base name generated from keywords
        
        Returns:
            Enhanced folder name
        """
        # Define theme patterns
        themes = {
            'Technology': ['code', 'software', 'programming', 'computer', 'algorithm',
                          'function', 'data', 'system', 'development', 'api'],
            'Science': ['research', 'study', 'experiment', 'theory', 'scientific',
                       'hypothesis', 'analysis', 'discovery', 'physics', 'chemistry'],
            'Space': ['space', 'planet', 'star', 'galaxy', 'universe', 'cosmic',
                     'astronomy', 'orbit', 'solar', 'mars', 'moon'],
            'Cooking': ['recipe', 'cook', 'food', 'ingredient', 'dish', 'meal',
                       'kitchen', 'flavor', 'taste', 'cuisine'],
            'History': ['history', 'historical', 'ancient', 'century', 'war',
                       'civilization', 'empire', 'dynasty', 'era', 'period'],
            'Finance': ['money', 'financial', 'investment', 'market', 'stock',
                       'economy', 'trading', 'profit', 'business', 'revenue'],
            'Sports': ['sport', 'game', 'team', 'player', 'match', 'score',
                      'championship', 'athlete', 'competition', 'tournament'],
            'Health': ['health', 'medical', 'disease', 'treatment', 'patient',
                      'doctor', 'medicine', 'therapy', 'diagnosis', 'clinical']
        }
        
        # Count theme matches
        theme_scores = {}
        for theme, keywords in themes.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                theme_scores[theme] = score
        
        # If a strong theme is detected, use it
        if theme_scores:
            top_theme = max(theme_scores, key=theme_scores.get)
            if theme_scores[top_theme] >= 3:  # Threshold for theme detection
                return top_theme
        
        return base_name
    
    def _clean_name(self, name: str) -> str:
        """
        Clean and validate a generated folder name.
        
        Args:
            name: Raw generated name
        
        Returns:
            Cleaned folder name
        """
        # Remove extra whitespace
        name = " ".join(name.split())
        
        # Capitalize first letter of each word
        name = " ".join(word.capitalize() for word in name.split())
        
        # Limit length
        if len(name) > 30:
            words = name.split()
            name = " ".join(words[:3])
        
        # Ensure it's not empty
        if not name or name.isspace():
            name = "Uncategorized"
        
        return name
