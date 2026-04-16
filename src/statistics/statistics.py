def compute_z_score(residuals):
    """
    zscore > 0 → overperformed vs model
    zscore < 0 → underperformed
    :param residuals:
    :return:
    """
    residual_mean = residuals.mean(axis=1, keepdims=True)
    residual_std = residuals.std(axis=1, keepdims=True)
    zscore = (residuals - residual_mean) / residual_std
    return zscore
