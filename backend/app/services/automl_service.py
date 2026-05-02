"""
AutoML Service
Standalone training service for selecting and training baseline ML models.
"""
import io
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from joblib import dump
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.services.firestore_service import get_firestore_service
from app.services.storage import get_storage_service


logger = logging.getLogger(__name__)


def _build_one_hot_encoder() -> OneHotEncoder:
    """Create OneHotEncoder compatible with multiple sklearn versions."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


class AutoMLService:
    """Service for AutoML listing, schema profiling, training, and artifact download."""

    def __init__(self) -> None:
        self.firestore_service = get_firestore_service()
        self.storage_service = get_storage_service()
        self.artifacts_root = Path(__file__).resolve().parents[2] / "automl_artifacts"
        self.artifacts_root.mkdir(parents=True, exist_ok=True)
        self._run_registry: Dict[str, Dict[str, str]] = {}

    def list_completed_files(self, user_id: str, limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
        """Return completed history records for AutoML picker."""
        records = self.firestore_service.get_user_completed_history(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

        items: List[Dict[str, Any]] = []
        for record in records:
            items.append(
                {
                    "history_id": record.get("history_id"),
                    "original_file_name": record.get("original_file", {}).get("file_name", "Unknown"),
                    "processed_file_name": record.get("processed_file", {}).get("file_name"),
                    "file_type": record.get("file_type", "unknown"),
                    "status": record.get("status", "unknown"),
                    "created_at": record.get("created_at", ""),
                }
            )
        return items

    def get_dataset_schema(self, user_id: str, history_id: str) -> Dict[str, Any]:
        """Load processed dataset and return profile + target candidates."""
        record = self._get_success_history_record(user_id=user_id, history_id=history_id)
        dataframe = self._load_processed_dataframe(record=record, user_id=user_id)

        rows, columns = dataframe.shape
        target_candidates: List[str] = []
        column_profiles: List[Dict[str, Any]] = []

        for column in dataframe.columns:
            series = dataframe[column]
            missing_count = int(series.isna().sum())
            unique_count = int(series.nunique(dropna=True))
            missing_pct = round((missing_count / rows * 100.0) if rows > 0 else 0.0, 2)

            column_profiles.append(
                {
                    "name": str(column),
                    "dtype": str(series.dtype),
                    "missing_count": missing_count,
                    "missing_pct": missing_pct,
                    "unique_count": unique_count,
                    "is_numeric": bool(is_numeric_dtype(series)),
                }
            )

            if unique_count > 1 and int(series.notna().sum()) > 0:
                target_candidates.append(str(column))

        return {
            "history_id": history_id,
            "original_file_name": record.get("original_file", {}).get("file_name", "Unknown"),
            "processed_file_name": record.get("processed_file", {}).get("file_name"),
            "rows": int(rows),
            "columns": int(columns),
            "target_candidates": target_candidates,
            "column_profiles": column_profiles,
        }

    def train_best_model(
        self,
        user_id: str,
        history_id: str,
        target_column: str,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Train candidate models, rank them, and persist best model artifact."""
        record = self._get_success_history_record(user_id=user_id, history_id=history_id)
        dataframe = self._load_processed_dataframe(record=record, user_id=user_id)

        if target_column not in dataframe.columns:
            raise ValueError(f"Target column '{target_column}' not found in processed dataset")

        if dataframe.shape[0] < 20:
            raise ValueError("Dataset has too few rows for train/test split. Minimum required: 20 rows.")

        working_df = dataframe.copy()
        working_df = working_df.dropna(subset=[target_column])

        if working_df.shape[0] < 20:
            raise ValueError("Target column has too many missing values. Need at least 20 non-null target rows.")

        y = working_df[target_column]
        X = working_df.drop(columns=[target_column])

        if X.shape[1] == 0:
            raise ValueError("No feature columns available after removing target column.")

        problem_type = self._detect_problem_type(y)

        if problem_type == "classification":
            if int(y.nunique(dropna=True)) < 2:
                raise ValueError("Classification target must contain at least 2 classes.")
            if is_object_dtype(y) or is_categorical_dtype(y):
                y = y.astype(str)

        X_train, X_test, y_train, y_test = self._split_data(
            X=X,
            y=y,
            problem_type=problem_type,
            test_size=test_size,
            random_state=random_state,
        )

        if problem_type == "regression" and int(y_test.shape[0]) < 2:
            raise ValueError("Regression requires at least 2 test rows. Increase test size or dataset rows.")

        feature_preprocessor = self._build_feature_preprocessor(X_train)
        model_specs = self._get_model_specs(problem_type=problem_type, random_state=random_state)

        leaderboard: List[Dict[str, Any]] = []
        best_entry: Optional[Dict[str, Any]] = None
        best_pipeline: Optional[Pipeline] = None

        for model_key, model_name, estimator in model_specs:
            started_at = time.perf_counter()
            try:
                pipeline = Pipeline(
                    steps=[
                        ("preprocessor", feature_preprocessor),
                        ("model", estimator),
                    ]
                )
                pipeline.fit(X_train, y_train)

                y_pred = pipeline.predict(X_test)
                y_prob = None
                if problem_type == "classification" and hasattr(pipeline, "predict_proba"):
                    try:
                        y_prob = pipeline.predict_proba(X_test)
                    except Exception:
                        y_prob = None

                metrics = self._evaluate_predictions(
                    problem_type=problem_type,
                    y_true=y_test,
                    y_pred=y_pred,
                    y_prob=y_prob,
                )

                score = self._score_from_metrics(problem_type=problem_type, metrics=metrics)
                if score is not None and (pd.isna(score) or score == float("inf") or score == float("-inf")):
                    score = None
                fit_time = round(time.perf_counter() - started_at, 4)

                entry = {
                    "rank": None,
                    "model_key": model_key,
                    "model_name": model_name,
                    "fit_time_seconds": fit_time,
                    "score": score,
                    "metrics": metrics,
                    "status": "success",
                    "error": None,
                    "is_best": False,
                }
                leaderboard.append(entry)

                if best_entry is None or (score is not None and score > (best_entry.get("score") or float("-inf"))):
                    best_entry = entry
                    best_pipeline = pipeline

            except Exception as exc:
                fit_time = round(time.perf_counter() - started_at, 4)
                leaderboard.append(
                    {
                        "rank": None,
                        "model_key": model_key,
                        "model_name": model_name,
                        "fit_time_seconds": fit_time,
                        "score": None,
                        "metrics": {},
                        "status": "failed",
                        "error": str(exc),
                        "is_best": False,
                    }
                )

        successful = [entry for entry in leaderboard if entry.get("status") == "success" and entry.get("score") is not None]
        successful.sort(key=lambda item: float(item["score"]), reverse=True)

        for idx, entry in enumerate(successful, start=1):
            entry["rank"] = idx

        failed = [entry for entry in leaderboard if entry.get("status") != "success" or entry.get("score") is None]
        ordered_leaderboard = successful + failed

        if not successful or best_entry is None or best_pipeline is None:
            raise RuntimeError("All candidate models failed to train. Please verify your target column and data quality.")

        best_entry["is_best"] = True
        for entry in ordered_leaderboard:
            if entry is best_entry:
                continue
            entry["is_best"] = False

        run_id, artifact_filename = self._persist_best_model(
            user_id=user_id,
            target_column=target_column,
            problem_type=problem_type,
            pipeline=best_pipeline,
            feature_columns=[str(column) for column in X.columns.tolist()],
        )

        return {
            "run_id": run_id,
            "history_id": history_id,
            "original_file_name": record.get("original_file", {}).get("file_name", "Unknown"),
            "processed_file_name": record.get("processed_file", {}).get("file_name"),
            "target_column": target_column,
            "problem_type": problem_type,
            "train_rows": int(X_train.shape[0]),
            "test_rows": int(X_test.shape[0]),
            "feature_count": int(X.shape[1]),
            "test_size": float(test_size),
            "leaderboard": ordered_leaderboard,
            "best_model": {
                "model_key": best_entry["model_key"],
                "model_name": best_entry["model_name"],
                "score": float(best_entry["score"]),
                "metrics": best_entry["metrics"],
            },
            "download_endpoint": f"/api/automl/download/{run_id}",
            "trained_at": datetime.utcnow().isoformat() + "Z",
            "artifact_file_name": artifact_filename,
        }

    def get_artifact_for_user(self, run_id: str, user_id: str) -> Optional[Tuple[Path, str]]:
        """Resolve model artifact path for a user."""
        run_info = self._run_registry.get(run_id)
        if run_info and run_info.get("user_id") == user_id:
            path = Path(run_info["path"])
            if path.exists():
                return path, run_info.get("file_name", path.name)

        user_dir = self.artifacts_root / user_id
        if not user_dir.exists():
            return None

        matches = sorted(user_dir.glob(f"{run_id}_*.joblib"))
        if not matches:
            return None

        artifact_path = matches[0]
        return artifact_path, artifact_path.name

    def _persist_best_model(
        self,
        user_id: str,
        target_column: str,
        problem_type: str,
        pipeline: Pipeline,
        feature_columns: List[str],
    ) -> Tuple[str, str]:
        run_id = uuid.uuid4().hex[:12]
        safe_target = self._sanitize_name(target_column)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{run_id}_{safe_target}_{problem_type}_{timestamp}.joblib"

        user_dir = self.artifacts_root / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = user_dir / filename

        payload = {
            "pipeline": pipeline,
            "target_column": target_column,
            "problem_type": problem_type,
            "feature_columns": feature_columns,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        dump(payload, artifact_path)

        self._run_registry[run_id] = {
            "user_id": user_id,
            "path": str(artifact_path),
            "file_name": filename,
        }
        return run_id, filename

    def _split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        problem_type: str,
        test_size: float,
        random_state: int,
    ):
        if problem_type == "classification":
            try:
                return train_test_split(
                    X,
                    y,
                    test_size=test_size,
                    random_state=random_state,
                    stratify=y,
                )
            except Exception:
                return train_test_split(
                    X,
                    y,
                    test_size=test_size,
                    random_state=random_state,
                    stratify=None,
                )

        return train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
        )

    def _get_model_specs(self, problem_type: str, random_state: int):
        if problem_type == "classification":
            return [
                ("logistic_regression", "Logistic Regression", LogisticRegression(max_iter=2000, class_weight="balanced")),
                ("random_forest", "Random Forest Classifier", RandomForestClassifier(n_estimators=300, random_state=random_state, n_jobs=-1)),
                ("gradient_boosting", "Gradient Boosting Classifier", GradientBoostingClassifier(random_state=random_state)),
            ]

        return [
            ("linear_regression", "Linear Regression", LinearRegression()),
            ("random_forest", "Random Forest Regressor", RandomForestRegressor(n_estimators=300, random_state=random_state, n_jobs=-1)),
            ("gradient_boosting", "Gradient Boosting Regressor", GradientBoostingRegressor(random_state=random_state)),
        ]

    def _build_feature_preprocessor(self, X: pd.DataFrame) -> ColumnTransformer:
        numeric_features = [
            str(col)
            for col in X.columns
            if is_numeric_dtype(X[col]) or is_bool_dtype(X[col])
        ]
        categorical_features = [str(col) for col in X.columns if str(col) not in numeric_features]

        transformers = []
        if numeric_features:
            transformers.append(
                (
                    "num",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    numeric_features,
                )
            )

        if categorical_features:
            transformers.append(
                (
                    "cat",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("onehot", _build_one_hot_encoder()),
                        ]
                    ),
                    categorical_features,
                )
            )

        if not transformers:
            raise ValueError("No usable feature columns found for AutoML training.")

        return ColumnTransformer(transformers=transformers)

    def _evaluate_predictions(
        self,
        problem_type: str,
        y_true: pd.Series,
        y_pred,
        y_prob=None,
    ) -> Dict[str, Optional[float]]:
        if problem_type == "classification":
            metrics: Dict[str, Optional[float]] = {
                "accuracy": float(accuracy_score(y_true, y_pred)),
                "precision_weighted": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
                "recall_weighted": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
                "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
                "roc_auc_ovr": None,
            }

            unique_classes = int(pd.Series(y_true).nunique())
            if y_prob is not None and unique_classes >= 2:
                try:
                    if getattr(y_prob, "ndim", 0) == 2 and y_prob.shape[1] == 2:
                        metrics["roc_auc_ovr"] = float(roc_auc_score(y_true, y_prob[:, 1]))
                    elif getattr(y_prob, "ndim", 0) == 2 and y_prob.shape[1] > 2:
                        metrics["roc_auc_ovr"] = float(
                            roc_auc_score(y_true, y_prob, multi_class="ovr", average="weighted")
                        )
                except Exception:
                    metrics["roc_auc_ovr"] = None

            return metrics

        rmse = mean_squared_error(y_true, y_pred, squared=False)
        return {
            "r2": float(r2_score(y_true, y_pred)),
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "rmse": float(rmse),
        }

    def _score_from_metrics(self, problem_type: str, metrics: Dict[str, Optional[float]]) -> Optional[float]:
        if problem_type == "classification":
            return metrics.get("f1_weighted")
        return metrics.get("r2")

    def _detect_problem_type(self, y: pd.Series) -> str:
        if is_bool_dtype(y) or is_object_dtype(y) or is_categorical_dtype(y):
            return "classification"

        if is_numeric_dtype(y):
            unique_count = int(y.nunique(dropna=True))
            row_count = int(y.shape[0])
            threshold = max(20, int(row_count * 0.05))
            if unique_count <= threshold:
                return "classification"
            return "regression"

        return "classification"

    def _get_success_history_record(self, user_id: str, history_id: str) -> Dict[str, Any]:
        record = self.firestore_service.get_history_by_id(history_id=history_id, user_id=user_id)
        if not record:
            raise ValueError("History record not found or access denied.")

        if record.get("status") != "success":
            raise ValueError("AutoML can run only on successfully processed files.")

        if not record.get("processed_file"):
            raise ValueError("Processed file information not available for this history record.")

        return record

    def _load_processed_dataframe(self, record: Dict[str, Any], user_id: str) -> pd.DataFrame:
        file_bytes, source_ref = self._download_processed_file_bytes(record=record, user_id=user_id)
        filename = record.get("processed_file", {}).get("file_name") or "processed.csv"
        logger.info(f"Loaded processed dataset bytes for AutoML from {source_ref}")
        return self._read_dataframe(file_bytes=file_bytes, file_name=filename)

    def _download_processed_file_bytes(self, record: Dict[str, Any], user_id: str) -> Tuple[bytes, str]:
        processed = record.get("processed_file") or {}
        bucket_name = self.storage_service.bucket_processed
        bucket_path = processed.get("bucket_path") or ""
        file_url = processed.get("file_url") or ""
        file_id = record.get("file_id")

        candidate_paths: List[str] = []

        if isinstance(bucket_path, str) and bucket_path.strip():
            cleaned = bucket_path.strip().lstrip("/")
            candidate_paths.append(cleaned)
            if not cleaned.startswith(f"{user_id}/"):
                candidate_paths.append(f"{user_id}/{Path(cleaned).name}")

        if file_id:
            try:
                listed = self.storage_service.client.storage.from_(bucket_name).list(f"{user_id}/")
                if isinstance(listed, list):
                    matches: List[str] = []
                    for entry in listed:
                        if not isinstance(entry, dict):
                            continue
                        name = entry.get("name")
                        if not isinstance(name, str):
                            continue
                        if file_id in name and "_processed_" in name:
                            matches.append(f"{user_id}/{name}")
                    matches.sort(reverse=True)
                    candidate_paths.extend(matches)
            except Exception as exc:
                logger.warning(f"Could not list processed bucket objects for AutoML fallback: {exc}")

        # De-duplicate while preserving order.
        seen = set()
        unique_paths: List[str] = []
        for item in candidate_paths:
            if item and item not in seen:
                seen.add(item)
                unique_paths.append(item)

        for path in unique_paths:
            try:
                binary = self.storage_service.client.storage.from_(bucket_name).download(path)
                if isinstance(binary, (bytes, bytearray)) and len(binary) > 0:
                    return bytes(binary), path
            except Exception as exc:
                logger.warning(f"Failed to download processed file from bucket path '{path}': {exc}")

        if file_url:
            try:
                response = requests.get(file_url, timeout=60)
                if response.status_code == 200 and response.content:
                    return response.content, "signed_url"
            except Exception as exc:
                logger.warning(f"Failed to fetch processed file via signed URL: {exc}")

        raise RuntimeError(
            "Unable to download processed file for AutoML. "
            "The file URL may be expired or storage metadata may be outdated."
        )

    def _read_dataframe(self, file_bytes: bytes, file_name: str) -> pd.DataFrame:
        name = (file_name or "").lower()
        buffer = io.BytesIO(file_bytes)

        if name.endswith(".xlsx") or name.endswith(".xls"):
            df = pd.read_excel(buffer)
        else:
            try:
                df = pd.read_csv(buffer, low_memory=False)
            except UnicodeDecodeError:
                buffer.seek(0)
                df = pd.read_csv(buffer, encoding="latin1", low_memory=False)

        if df.empty:
            raise ValueError("Processed dataset is empty.")

        # Ensure all column names are strings.
        df.columns = [str(column) for column in df.columns]
        return df

    def _sanitize_name(self, value: str) -> str:
        if not value:
            return "target"
        safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value)
        safe = safe.strip("_")
        return safe[:64] or "target"


_automl_service: Optional[AutoMLService] = None


def get_automl_service() -> AutoMLService:
    """Get or create AutoML service singleton."""
    global _automl_service
    if _automl_service is None:
        _automl_service = AutoMLService()
    return _automl_service
