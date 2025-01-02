from loguru import logger
import numpy as np

class VectorManager:

    def __init__(self, embeddings=None):
        """
        Initialize with the precomputed embeddings dictionary.
        """
        self.embeddings = embeddings
        

    def vectorize(self, client, corpus):

        logger.info("Querying to get embeddings")

        # Generate embeddings
        try:
            embedings_response = client.generate_embeddings(corpus)

            # Extract only embeddings from the response
            embedings = [item.embedding for item in embedings_response.data]
            logger.success("Embeddings received and processed")
            return embedings
        
        except Exception as e:
            logger.error(f"An error occured while qurying OpenAI's Embedding Generator")


    def cosine_similarity(self, vec1, vec2):
        """
        Compute the cosine similarity between two vectors.
        """
        dot_product = np.dot(vec1, vec2)
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)
        return dot_product / (magnitude1 * magnitude2 + 1e-10)
    

    def retrieve_chunks(self, query_embeddings, top_k=5):
        """
        Retrieve the top_k most relevant chunks based on cosine similarity.

        Args:
            query_embeddings: The embedding vector of the query.
            top_k: The number of top results to retrieve.

        Returns:
            List of the most relevant chunks across all data types.
        """
        data_types = ["text_embeddings", "table_embeddings", "article_embeddings"]
        try:
            top_chunks = []

            for data_type in data_types:
                if data_type not in self.embeddings:
                    logger.warning(f"Data type '{data_type}' not found in embeddings. Skipping.")
                    continue

                # Compute similarity for all embeddings of the current data type
                similarities = []
                for item in self.embeddings[data_type]:
                    similarity = self.cosine_similarity(query_embeddings, item["embedding"])
                    similarities.append({"data": item, "similarity": similarity})

                # Sort by similarity in descending order
                sorted_similarities = sorted(similarities, key=lambda x: x["similarity"], reverse=True)

                # Append top_k chunks
                top_chunks.extend([entry["data"] for entry in sorted_similarities[:top_k]])

            return top_chunks

        except Exception as e:
            logger.error(f"An error occurred while retrieving chunks: {e}")
            return []

        