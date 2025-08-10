#!/usr/bin/env python3
"""
Optimized Semantic Search Service
Pure Sentence Transformers + FAISS implementation
Focused on performance and accuracy
"""

import numpy as np
import faiss
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from datetime import datetime
import pickle
import os

logger = logging.getLogger(__name__)

class OptimizedSemanticService:
    """
    High-performance semantic search service using Sentence Transformers
    - Optimized text preprocessing
    - Efficient FAISS indexing
    - Smart caching and batching
    - Pure semantic search focus
    """
    
    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 index_dir: str = None,
                 cache_embeddings: bool = True):
        """Initialize the optimized semantic service"""
        self.model_name = model_name
        self.index_dir = Path(index_dir) if index_dir else Path(__file__).parent.parent / "data" / "vector_index"
        self.cache_embeddings = cache_embeddings
        
        # Ensure index directory exists
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.index_file = self.index_dir / "optimized_faiss_index.bin"
        self.metadata_file = self.index_dir / "optimized_metadata.pkl"
        self.embeddings_file = self.index_dir / "optimized_embeddings.npy"
        
        # Core components
        self.model = None
        self.index = None
        self.offer_embeddings = None
        self.offer_metadata = []
        self.offers = []
        
        # Performance metrics
        self.search_times = []
        self.embedding_times = []
        
        # Initialize
        self._load_model()
        self._load_or_build_index()
    
    def _load_model(self):
        """Load the Sentence Transformer model"""
        try:
            logger.info(f"🤖 Loading Sentence Transformer: {self.model_name}")
            start_time = time.time()
            
            self.model = SentenceTransformer(self.model_name)
            
            load_time = time.time() - start_time
            logger.info(f"✅ Model loaded in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def _load_or_build_index(self):
        """Load existing index or build new one"""
        if self._try_load_existing_index():
            logger.info("✅ Loaded existing optimized index")
        else:
            logger.info("🔨 Building new optimized index...")
            self._load_offers()
            self._build_optimized_index()
    
    def _try_load_existing_index(self) -> bool:
        """Try to load existing index files"""
        try:
            if (self.index_file.exists() and 
                self.metadata_file.exists() and 
                self.embeddings_file.exists()):
                
                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    self.offer_metadata = pickle.load(f)
                
                # Load embeddings
                self.offer_embeddings = np.load(self.embeddings_file)
                
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_file))
                
                logger.info(f"📊 Loaded index with {len(self.offer_metadata)} offers")
                return True
                
        except Exception as e:
            logger.warning(f"Failed to load existing index: {e}")
        
        return False
    
    def _load_offers(self):
        """Load travel offers from data files"""
        data_dir = Path(__file__).parent.parent / "data"
        
        # Load offers from different regions
        regions = ['asia', 'europe', 'americas', 'africa', 'oceania']
        
        for region in regions:
            region_dir = data_dir / region
            if region_dir.exists():
                for json_file in region_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            region_offers = json.load(f)
                            if isinstance(region_offers, list):
                                self.offers.extend(region_offers)
                            elif isinstance(region_offers, dict) and 'offers' in region_offers:
                                self.offers.extend(region_offers['offers'])
                    except Exception as e:
                        logger.warning(f"Failed to load {json_file}: {e}")
        
        logger.info(f"📊 Loaded {len(self.offers)} offers")
    
    def _create_optimized_text_representation(self, offer: Dict[str, Any]) -> str:
        """
        Create optimized text representation for semantic search
        Focuses on key semantic elements
        """
        text_parts = []
        
        # Product name (highest weight)
        if offer.get('product_name'):
            text_parts.append(f"product: {offer['product_name']}")
        
        # Destinations (high weight)
        if offer.get('destinations'):
            dest_texts = []
            for dest in offer['destinations']:
                if isinstance(dest, dict):
                    if dest.get('city'):
                        dest_texts.append(dest['city'])
                    if dest.get('country'):
                        dest_texts.append(dest['country'])
                elif isinstance(dest, str):
                    dest_texts.append(dest)
            
            if dest_texts:
                text_parts.append(f"destination: {' '.join(dest_texts)}")
        
        # Highlights (medium weight)
        if offer.get('highlights'):
            highlights = offer['highlights']
            if isinstance(highlights, list):
                highlight_texts = []
                for highlight in highlights:
                    if isinstance(highlight, str):
                        highlight_texts.append(highlight)
                    elif isinstance(highlight, dict) and highlight.get('text'):
                        highlight_texts.append(highlight['text'])
                
                if highlight_texts:
                    text_parts.append(f"highlights: {' '.join(highlight_texts)}")
            elif isinstance(highlights, str):
                text_parts.append(f"highlights: {highlights}")
        
        # Description (medium weight)
        if offer.get('description'):
            text_parts.append(f"description: {offer['description']}")
        
        # Offer type and travel style (low weight)
        if offer.get('offer_type'):
            text_parts.append(f"type: {offer['offer_type']}")
        
        if offer.get('travel_style'):
            text_parts.append(f"style: {offer['travel_style']}")
        
        # Duration (contextual)
        if offer.get('duration'):
            text_parts.append(f"duration: {offer['duration']} days")
        
        return " ".join(text_parts)
    
    def _build_optimized_index(self):
        """Build optimized FAISS index with better text representations"""
        if not self.offers:
            logger.warning("No offers loaded, skipping index creation")
            return
        
        try:
            logger.info("🔨 Building optimized index...")
            start_time = time.time()
            
            # Clear existing data
            self.offer_metadata = []
            self.offer_embeddings = None
            self.index = None
            
            # Create optimized text representations
            offer_texts = []
            logger.info("📝 Creating text representations...")
            
            for i, offer in enumerate(self.offers):
                # Create optimized text representation
                text_representation = self._create_optimized_text_representation(offer)
                offer_texts.append(text_representation)
                
                # Store metadata
                self.offer_metadata.append({
                    'index': i,
                    'offer': offer,
                    'text': text_representation,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Progress logging
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(self.offers)} offers")
            
            # Generate embeddings
            logger.info("🧠 Generating embeddings...")
            embedding_start = time.time()
            
            # Use batch processing for better performance
            batch_size = 32
            all_embeddings = []
            
            for i in range(0, len(offer_texts), batch_size):
                batch_texts = offer_texts[i:i + batch_size]
                batch_embeddings = self.model.encode(batch_texts, show_progress_bar=False)
                all_embeddings.append(batch_embeddings)
                
                if (i + batch_size) % 100 == 0:
                    logger.info(f"Generated embeddings for {min(i + batch_size, len(offer_texts))}/{len(offer_texts)} offers")
            
            # Combine all embeddings
            self.offer_embeddings = np.vstack(all_embeddings).astype('float32')
            
            embedding_time = time.time() - embedding_start
            logger.info(f"✅ Generated {len(self.offer_embeddings)} embeddings in {embedding_time:.2f}s")
            
            # Build FAISS index
            logger.info("🔧 Building FAISS index...")
            dimension = self.offer_embeddings.shape[1]
            
            # Use IndexFlatIP for inner product (cosine similarity after normalization)
            self.index = faiss.IndexFlatIP(dimension)
            
            # Normalize embeddings for better cosine similarity
            faiss.normalize_L2(self.offer_embeddings)
            self.index.add(self.offer_embeddings)
            
            # Save index
            self._save_index()
            
            total_time = time.time() - start_time
            logger.info(f"✅ Optimized index built in {total_time:.2f}s")
            logger.info(f"📊 Index contains {len(self.offer_embeddings)} offers with {dimension}D embeddings")
            
        except Exception as e:
            logger.error(f"❌ Failed to build optimized index: {e}")
            raise
    
    def _save_index(self):
        """Save the optimized index to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.offer_metadata, f)
            
            # Save embeddings
            np.save(self.embeddings_file, self.offer_embeddings)
            
            logger.info("💾 Index saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save index: {e}")
    
    def search(self, query: str, top_k: int = 10, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        Perform semantic search with optimized performance
        """
        if not self.index or self.offer_embeddings is None:
            logger.error("Index not built")
            return []
        
        try:
            search_start = time.time()
            
            # Generate query embedding
            query_embedding = self.model.encode([query])
            query_embedding = query_embedding.astype('float32')
            
            # Normalize query embedding for cosine similarity
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index (get more candidates for better filtering)
            search_k = min(top_k * 3, len(self.offer_metadata))
            similarities, indices = self.index.search(query_embedding, search_k)
            
            # Convert numpy arrays to regular Python types
            similarities_list = similarities[0].tolist()
            indices_list = indices[0].tolist()
            
            # Filter and format results
            results = []
            seen_offers = set()
            
            for similarity, idx in zip(similarities_list, indices_list):
                if idx < len(self.offer_metadata) and similarity >= threshold:
                    offer_data = self.offer_metadata[idx]['offer'].copy()
                    offer_data['similarity_score'] = float(similarity)
                    offer_data['search_rank'] = len(results) + 1
                    
                    # Avoid duplicates
                    offer_id = offer_data.get('reference', f'offer_{idx}')
                    if offer_id not in seen_offers:
                        seen_offers.add(offer_id)
                        results.append(offer_data)
                        
                        if len(results) >= top_k:
                            break
            
            search_time = time.time() - search_start
            self.search_times.append(search_time)
            
            logger.info(f"🔍 Found {len(results)} offers for '{query}' in {search_time:.3f}s")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_with_context(self, query: str, context: str = "", top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search with additional context for better relevance
        """
        # Combine query with context
        enhanced_query = f"{query} {context}".strip()
        return self.search(enhanced_query, top_k)
    
    def get_similar_offers(self, offer_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find offers similar to a specific offer"""
        # Find the target offer
        target_idx = None
        for i, metadata in enumerate(self.offer_metadata):
            if metadata['offer'].get('reference') == offer_id:
                target_idx = i
                break
        
        if target_idx is None:
            logger.warning(f"Offer {offer_id} not found")
            return []
        
        # Get the target embedding
        target_embedding = self.offer_embeddings[target_idx:target_idx+1]
        
        # Search for similar offers
        similarities, indices = self.index.search(target_embedding, top_k + 1)  # +1 to exclude self
        
        results = []
        for similarity, idx in zip(similarities[0], indices[0]):
            if idx != target_idx and idx < len(self.offer_metadata):
                offer_data = self.offer_metadata[idx]['offer'].copy()
                offer_data['similarity_score'] = float(similarity)
                results.append(offer_data)
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_search_time = np.mean(self.search_times) if self.search_times else 0
        avg_embedding_time = np.mean(self.embedding_times) if self.embedding_times else 0
        
        return {
            'total_offers': len(self.offers),
            'indexed_offers': len(self.offer_metadata),
            'embedding_dimension': self.offer_embeddings.shape[1] if self.offer_embeddings is not None else 0,
            'index_built': self.index is not None,
            'model_name': self.model_name,
            'average_search_time': avg_search_time,
            'average_embedding_time': avg_embedding_time,
            'total_searches': len(self.search_times),
            'index_file_size': self.index_file.stat().st_size if self.index_file.exists() else 0,
            'embeddings_file_size': self.embeddings_file.stat().st_size if self.embeddings_file.exists() else 0
        }
    
    def clear_cache(self):
        """Clear performance cache"""
        self.search_times = []
        self.embedding_times = []
        logger.info("🧹 Performance cache cleared")
    
    def rebuild_index(self, force: bool = False):
        """Rebuild the index"""
        if force or not self.index:
            logger.info("🔨 Rebuilding index...")
            self._load_offers()
            self._build_optimized_index()
        else:
            logger.info("✅ Index already exists, use force=True to rebuild") 