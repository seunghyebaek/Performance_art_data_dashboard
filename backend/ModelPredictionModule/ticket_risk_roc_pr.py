from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.preprocessing import label_binarize

def compute_roc_pr(y_true, y_proba, num_classes=3):
    """
    y_true: 실제 레이블 (정수 배열), 예) [0, 2, 1, 0, ...]
    y_proba: 모델이 반환한 예측 확률 (2D 배열: (n_samples, num_classes))
    num_classes: 분류할 클래스 수 (여기서는 3)
    """
    # 다중 클래스의 경우, 실제 레이블을 이진 형식으로 변환합니다.
    y_true_bin = label_binarize(y_true, classes=list(range(num_classes)))
    roc_data = []
    pr_data = []
    
    for i in range(num_classes):
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_proba[:, i])
        precision, recall, _ = precision_recall_curve(y_true_bin[:, i], y_proba[:, i])
        
        roc_data.append({
            "class": i,
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist()
        })
        pr_data.append({
            "class": i,
            "precision": precision.tolist(),
            "recall": recall.tolist()
        })
        
    return {
        "roc_curve": roc_data,
        "pr_curve": pr_data
    }
