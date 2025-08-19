from typing import List



class MMRSelector:
    def __init__(self,
                 final_k: int = 8,
                 lambda_param: float = 0.5,
                 similarity_threshold: float = 0.3):
        """
        Configure post-retrieval filtering and diversification.

        :param final_k: Number of items to select.
        :param lambda_param: 0 = pure diversity, 1 = pure relevance.
        :param similarity_threshold: Minimum cosine similarity threshold.
        """
        self.final_k = final_k
        self.lambda_param = lambda_param
        self.similarity_threshold = similarity_threshold

    @staticmethod
    def _dot(u: List[float], v: List[float]) -> float:
        return sum(a * b for a, b in zip(u, v))

    @classmethod
    def _norm(cls, u: List[float]) -> float:
        return (cls._dot(u, u) or 1.0) ** 0.5

    @classmethod
    def _cosine(cls, u: List[float], v: List[float]) -> float:
        return cls._dot(u, v) / (cls._norm(u) * cls._norm(v))

    def select(self, query_vec: List[float], doc_vecs: List[List[float]]) -> List[int]:
        """
        Perform Maximal Marginal Relevance (MMR) selection.

        :param query_vec: Vector representing the query.
        :param doc_vecs: List of document vectors.
        :return: Indices of selected documents.
        """
        selected: List[int] = []
        candidates = list(range(len(doc_vecs)))
        relevance = [self._cosine(query_vec, d) for d in doc_vecs]

        while candidates and len(selected) < self.final_k:
            if not selected:
                best = max(candidates, key=lambda i: relevance[i])
            else:
                best = max(
                    candidates,
                    key=lambda i: self.lambda_param * relevance[i]
                    - (1.0 - self.lambda_param)
                    * max(self._cosine(doc_vecs[i], doc_vecs[j]) for j in selected),
                )
            # Enforce similarity threshold
            if relevance[best] >= self.similarity_threshold:
                selected.append(best)
            candidates.remove(best)

        return selected
