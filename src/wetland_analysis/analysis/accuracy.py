"""
Accuracy assessment functions for wetland classification.
"""

import xarray as xr
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from sklearn.metrics import confusion_matrix, cohen_kappa_score

logger = logging.getLogger(__name__)


def calculate_confusion_matrix(
    reference: Union[xr.DataArray, np.ndarray],
    prediction: Union[xr.DataArray, np.ndarray],
    classes: Optional[List[int]] = None
) -> np.ndarray:
    """
    Calculate confusion matrix between reference and prediction.

    Parameters
    ----------
    reference : xr.DataArray or np.ndarray
        Reference (ground truth) data
    prediction : xr.DataArray or np.ndarray
        Predicted (model) data
    classes : list of int, optional
        List of class labels. If None, inferred from data.

    Returns
    -------
    np.ndarray
        Confusion matrix
    """
    # Convert to numpy arrays if needed
    if isinstance(reference, xr.DataArray):
        ref_flat = reference.values.ravel()
    else:
        ref_flat = reference.ravel()

    if isinstance(prediction, xr.DataArray):
        pred_flat = prediction.values.ravel()
    else:
        pred_flat = prediction.ravel()

    # Remove NaN values
    valid_mask = ~np.isnan(ref_flat) & ~np.isnan(pred_flat)
    ref_valid = ref_flat[valid_mask]
    pred_valid = pred_flat[valid_mask]

    if len(ref_valid) == 0:
        logger.warning("No valid pixels for confusion matrix calculation")
        return np.array([])

    # Get class labels
    if classes is None:
        classes = sorted(set(np.unique(ref_valid)) | set(np.unique(pred_valid)))

    # Calculate confusion matrix
    cm = confusion_matrix(ref_valid, pred_valid, labels=classes)

    logger.info(f"Confusion matrix calculated with {len(ref_valid)} valid pixels")
    return cm


def calculate_classification_metrics(
    confusion_mat: np.ndarray,
    class_labels: Optional[List[str]] = None
) -> Dict[str, Union[float, Dict[str, float]]]:
    """
    Calculate classification metrics from confusion matrix.

    Parameters
    ----------
    confusion_mat : np.ndarray
        Confusion matrix (n_classes x n_classes)
    class_labels : list of str, optional
        Names for each class

    Returns
    -------
    dict
        Dictionary containing overall and per-class metrics
    """
    n_classes = confusion_mat.shape[0]

    # Overall metrics
    total_pixels = confusion_mat.sum()
    correct_pixels = np.trace(confusion_mat)
    overall_accuracy = correct_pixels / total_pixels if total_pixels > 0 else 0.0

    # Cohen's Kappa
    expected_accuracy = np.sum(confusion_mat.sum(axis=0) * confusion_mat.sum(axis=1)) / (total_pixels ** 2)
    kappa = (overall_accuracy - expected_accuracy) / (1 - expected_accuracy) if total_pixels > 0 else 0.0

    # Per-class metrics
    per_class_metrics = {}
    for i in range(n_classes):
        tp = confusion_mat[i, i]
        fp = confusion_mat[:, i].sum() - tp
        fn = confusion_mat[i, :].sum() - tp
        tn = total_pixels - tp - fp - fn

        # Producer's Accuracy (Recall)
        pa = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # User's Accuracy (Precision)
        ua = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        # F1-Score
        f1 = 2 * pa * ua / (pa + ua) if (pa + ua) > 0 else 0.0

        # Intersection over Union (IoU)
        iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0

        class_name = class_labels[i] if class_labels else f"Class_{i}"
        per_class_metrics[class_name] = {
            'producer_accuracy': float(pa),
            'user_accuracy': float(ua),
            'f1_score': float(f1),
            'iou': float(iou),
            'true_positives': int(tp),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_negatives': int(tn)
        }

    metrics = {
        'overall_accuracy': float(overall_accuracy),
        'kappa': float(kappa),
        'total_pixels': int(total_pixels),
        'correct_pixels': int(correct_pixels),
        'per_class': per_class_metrics
    }

    logger.info(f"Calculated classification metrics: OA={overall_accuracy:.3f}, Kappa={kappa:.3f}")
    return metrics


def calculate_spatial_accuracy(
    reference: xr.DataArray,
    target: xr.DataArray,
    metrics: List[str] = None,
    classes: Optional[List[int]] = None,
    class_names: Optional[List[str]] = None
) -> Dict:
    """
    Calculate spatial accuracy metrics between two datasets.

    Parameters
    ----------
    reference : xr.DataArray
        Reference dataset (ground truth)
    target : xr.DataArray
        Target dataset to evaluate
    metrics : list of str, optional
        Metrics to calculate. Default: ['OA', 'Kappa', 'PA', 'UA', 'F1', 'IoU']
    classes : list of int, optional
        Class labels to include in analysis
    class_names : list of str, optional
        Names for each class

    Returns
    -------
    dict
        Dictionary containing accuracy metrics
    """
    if metrics is None:
        metrics = ['OA', 'Kappa', 'PA', 'UA', 'F1', 'IoU']

    # Ensure datasets have same shape
    if reference.shape != target.shape:
        raise ValueError(f"Shape mismatch: reference {reference.shape}, target {target.shape}")

    # Calculate confusion matrix
    cm = calculate_confusion_matrix(reference, target, classes)

    if cm.size == 0:
        logger.error("Could not calculate confusion matrix")
        return {}

    # Calculate metrics
    all_metrics = calculate_classification_metrics(cm, class_names)

    # Filter requested metrics
    result = {}
    for metric in metrics:
        metric_lower = metric.lower()
        if metric_lower == 'oa':
            result['overall_accuracy'] = all_metrics['overall_accuracy']
        elif metric_lower == 'kappa':
            result['kappa'] = all_metrics['kappa']
        elif metric_lower == 'pa':
            # Producer's Accuracy (per class)
            result['producer_accuracy'] = {
                cls: vals['producer_accuracy'] for cls, vals in all_metrics['per_class'].items()
            }
        elif metric_lower == 'ua':
            # User's Accuracy (per class)
            result['user_accuracy'] = {
                cls: vals['user_accuracy'] for cls, vals in all_metrics['per_class'].items()
            }
        elif metric_lower == 'f1':
            result['f1_score'] = {
                cls: vals['f1_score'] for cls, vals in all_metrics['per_class'].items()
            }
        elif metric_lower == 'iou':
            result['iou'] = {
                cls: vals['iou'] for cls, vals in all_metrics['per_class'].items()
            }
        else:
            logger.warning(f"Unknown metric: {metric}")

    # Add confusion matrix for reference
    result['confusion_matrix'] = cm.tolist()
    if class_names:
        result['class_labels'] = class_names
    if classes:
        result['classes'] = classes

    return result


def calculate_pixel_agreement(
    dataset1: xr.DataArray,
    dataset2: xr.DataArray,
    threshold: float = 0.5
) -> Dict[str, float]:
    """
    Calculate pixel-level agreement between two binary datasets.

    Parameters
    ----------
    dataset1 : xr.DataArray
        First binary dataset (0 or 1)
    dataset2 : xr.DataArray
        Second binary dataset (0 or 1)
    threshold : float, optional
        Threshold for binary classification (if data is continuous)

    Returns
    -------
    dict
        Agreement metrics
    """
    # Binarize if needed
    if dataset1.dtype != bool and dataset1.dtype != int:
        ds1_bin = (dataset1 > threshold).astype(int)
    else:
        ds1_bin = dataset1.astype(int)

    if dataset2.dtype != bool and dataset2.dtype != int:
        ds2_bin = (dataset2 > threshold).astype(int)
    else:
        ds2_bin = dataset2.astype(int)

    # Calculate agreement
    agreement = (ds1_bin == ds2_bin).sum().item()
    total_pixels = ds1_bin.size

    agreement_percent = agreement / total_pixels * 100

    # Calculate per-class agreement
    wetland_agreement = ((ds1_bin == 1) & (ds2_bin == 1)).sum().item()
    non_wetland_agreement = ((ds1_bin == 0) & (ds2_bin == 0)).sum().item()

    wetland_pixels_ds1 = (ds1_bin == 1).sum().item()
    wetland_pixels_ds2 = (ds2_bin == 1).sum().item()

    metrics = {
        'total_agreement_percent': float(agreement_percent),
        'total_agreement_pixels': int(agreement),
        'total_pixels': int(total_pixels),
        'wetland_agreement_pixels': int(wetland_agreement),
        'non_wetland_agreement_pixels': int(non_wetland_agreement),
        'wetland_pixels_dataset1': int(wetland_pixels_ds1),
        'wetland_pixels_dataset2': int(wetland_pixels_ds2),
        'wetland_area_difference': int(abs(wetland_pixels_ds1 - wetland_pixels_ds2))
    }

    logger.info(f"Pixel agreement: {agreement_percent:.2f}% ({agreement}/{total_pixels} pixels)")
    return metrics