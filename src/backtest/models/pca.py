import numpy as np
from sklearn.decomposition import PCA


def fit_pca(scaled_X: np.ndarray, n_components=2) -> tuple[PCA,np.ndarray, np.ndarray]:
    """
    PC1 represents the dominant factor driving co-movement among the commodities. If all prices tend to move together, PC1 captures that shared movement.
    PC2 is orthogonal to PC1 and explains the next largest variance, capturing patterns not explained by PC1.
    :return:
    """
    print(f'n_components:{n_components}')
    pca = PCA(n_components=n_components)
    principal_components = pca.fit_transform(scaled_X)
    print(f'principal components:\n{principal_components}')
    print(f'PCA components:\n{pca.components_}')
    print(f'PCA n components:\n{pca.n_components_}')
    residuals = get_residuals(pca, principal_components, scaled_X)
    return pca, principal_components, residuals

def get_residuals(pca, principal_components: np.ndarray, scaled_X: np.ndarray) -> np.ndarray:
    """
    Reconstructed Scaled Returns = PC ⋅ W^T
    :param pca:
    :param principal_components:
    :return:
    """
    reconstructed = np.dot(principal_components, pca.components_)
    residuals = scaled_X - reconstructed
    return residuals

