"""
Firebase Firestore Service
Manages user history records in Firestore
"""
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from firebase_admin import firestore
from app.utils.firebase_config import initialize_firebase
try:
    from google.cloud.firestore_v1.base_query import FieldFilter
except Exception:  # pragma: no cover - compatibility fallback
    FieldFilter = None

logger = logging.getLogger(__name__)

# Initialize Firebase (this ensures Firestore is available)
initialize_firebase()


class FirestoreService:
    """Service for managing Firestore database operations"""
    
    COLLECTION_HISTORY = "preprocessing_history"
    PREPROCESSING_VERSION = "v2.0"
    
    def __init__(self):
        """Initialize Firestore client"""
        try:
            self.db = firestore.client()
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {str(e)}")
            raise RuntimeError(f"Failed to initialize Firestore: {str(e)}")

    def _normalize_history_record(self, doc) -> Dict[str, Any]:
        """Normalize Firestore document to API-friendly dictionary"""
        data = doc.to_dict() or {}
        data["history_id"] = doc.id

        created_at = data.get("created_at")
        if created_at:
            data["created_at"] = created_at.isoformat()
        elif data.get("created_at_client"):
            data["created_at"] = data.get("created_at_client")

        return data

    def _where_equal(self, query, field: str, value: Any):
        """
        Apply equality filter using the preferred FieldFilter API when available,
        with fallback for older client versions.
        """
        if FieldFilter is not None:
            try:
                return query.where(filter=FieldFilter(field, "==", value))
            except Exception:
                pass
        return query.where(field, "==", value)

    def _compact_preprocessing_report(
        self,
        preprocessing_report: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """
        Compact preprocessing report for Firestore storage safety.
        mode: full | compact | minimal
        """
        report = dict(preprocessing_report or {})

        # Bound list sizes even in full mode.
        final_columns = report.get("final_columns")
        if isinstance(final_columns, list):
            report["final_columns_count"] = int(report.get("final_columns_count") or len(final_columns))
            report["final_columns"] = final_columns[:200]
            report["final_columns_truncated"] = len(final_columns) > 200

        dropped_columns = report.get("dropped_columns")
        if isinstance(dropped_columns, list):
            report["dropped_columns_count"] = int(len(dropped_columns))
            report["dropped_columns"] = dropped_columns[:200]
            report["dropped_columns_truncated"] = len(dropped_columns) > 200

        non_informative = report.get("non_informative_columns_removed")
        if isinstance(non_informative, list):
            report["non_informative_columns_removed_count"] = int(len(non_informative))
            report["non_informative_columns_removed"] = non_informative[:120]
            report["non_informative_columns_removed_truncated"] = len(non_informative) > 120

        profile = report.get("insights_profile")
        if not isinstance(profile, dict):
            return report

        compact_profile = dict(profile)
        if mode == "minimal":
            # Minimal mode must still preserve all core insight tabs.
            # We keep all sections with tight limits instead of dropping them.
            section_limits = {
                "column_details": 40,
                "missing_values_by_column": 40,
                "numerical_statistics": 10,
                "correlation_pairs": 20,
                "categorical_distributions": 8,
                "outlier_summary": 10,
                "highlights": 6,
                "correlation_matrix_columns": 10,
            }
            histogram_keep = False
            sample_values_keep = False
        elif mode == "compact":
            section_limits = {
                "column_details": 60,
                "missing_values_by_column": 60,
                "numerical_statistics": 16,
                "correlation_pairs": 25,
                "categorical_distributions": 10,
                "outlier_summary": 14,
                "highlights": 8,
                "correlation_matrix_columns": 12,
            }
            histogram_keep = True
            sample_values_keep = True
        else:
            section_limits = {
                "column_details": 80,
                "missing_values_by_column": 80,
                "numerical_statistics": 20,
                "correlation_pairs": 30,
                "categorical_distributions": 12,
                "outlier_summary": 20,
                "highlights": 10,
                "correlation_matrix_columns": 12,
            }
            histogram_keep = True
            sample_values_keep = True

        if isinstance(compact_profile.get("column_details"), list):
            compact_cols = []
            for col in compact_profile["column_details"][:section_limits["column_details"]]:
                if not isinstance(col, dict):
                    continue
                col_copy = dict(col)
                if isinstance(col_copy.get("sample_values"), list):
                    if sample_values_keep:
                        col_copy["sample_values"] = col_copy["sample_values"][:1]
                    else:
                        col_copy.pop("sample_values", None)
                compact_cols.append(col_copy)
            compact_profile["column_details"] = compact_cols

        if isinstance(compact_profile.get("missing_values_by_column"), list):
            compact_profile["missing_values_by_column"] = compact_profile["missing_values_by_column"][
                :section_limits["missing_values_by_column"]
            ]

        if isinstance(compact_profile.get("correlation_pairs"), list):
            compact_profile["correlation_pairs"] = compact_profile["correlation_pairs"][
                :section_limits["correlation_pairs"]
            ]

        if isinstance(compact_profile.get("categorical_distributions"), list):
            bounded_categories = []
            for item in compact_profile["categorical_distributions"][:section_limits["categorical_distributions"]]:
                if not isinstance(item, dict):
                    continue
                item_copy = dict(item)
                top_values = item_copy.get("top_values")
                if isinstance(top_values, list):
                    top_value_limit = 5 if mode == "minimal" else 8
                    item_copy["top_values"] = top_values[:top_value_limit]
                bounded_categories.append(item_copy)
            compact_profile["categorical_distributions"] = bounded_categories

        if isinstance(compact_profile.get("outlier_summary"), list):
            compact_profile["outlier_summary"] = compact_profile["outlier_summary"][:section_limits["outlier_summary"]]

        if isinstance(compact_profile.get("highlights"), list):
            compact_profile["highlights"] = compact_profile["highlights"][:section_limits["highlights"]]

        numerical_stats = compact_profile.get("numerical_statistics")
        if isinstance(numerical_stats, list):
            bounded_stats = []
            for stat in numerical_stats[:section_limits["numerical_statistics"]]:
                if not isinstance(stat, dict):
                    continue
                stat_copy = dict(stat)
                if isinstance(stat_copy.get("histogram"), list):
                    if histogram_keep:
                        hist_limit = 6 if mode != "full" else 8
                        stat_copy["histogram"] = stat_copy["histogram"][:hist_limit]
                    else:
                        stat_copy.pop("histogram", None)
                bounded_stats.append(stat_copy)
            compact_profile["numerical_statistics"] = bounded_stats

        corr_matrix = compact_profile.get("correlation_matrix")
        if isinstance(corr_matrix, dict):
            matrix_columns = corr_matrix.get("columns")
            matrix_values = corr_matrix.get("values")
            if isinstance(matrix_columns, list) and isinstance(matrix_values, list):
                limited_cols = matrix_columns[:section_limits["correlation_matrix_columns"]]
                max_size = len(limited_cols)
                # Firestore doesn't allow arrays containing arrays.
                # Store matrix rows as maps, then decode back to square values for API payloads.
                matrix_rows = []
                for row_idx in range(max_size):
                    source_row = matrix_values[row_idx] if row_idx < len(matrix_values) else []
                    if not isinstance(source_row, list):
                        source_row = []
                    row_values_map: Dict[str, Any] = {}
                    for col_idx in range(max_size):
                        col_name = limited_cols[col_idx]
                        row_values_map[col_name] = source_row[col_idx] if col_idx < len(source_row) else None

                    matrix_rows.append({
                        "column": limited_cols[row_idx],
                        "values": row_values_map,
                    })

                compact_profile["correlation_matrix"] = {
                    "columns": limited_cols,
                    "rows": matrix_rows,
                }

        compact_profile["storage_mode"] = mode

        if mode == "minimal":
            keep_keys = {
                "version",
                "generated_at",
                "dataset_overview",
                "data_type_distribution",
                "column_details",
                "missing_values_by_column",
                "numerical_statistics",
                "correlation_pairs",
                "correlation_matrix",
                "categorical_distributions",
                "outlier_summary",
                "highlights",
                "limits",
                "truncated",
                "storage_mode",
            }
            compact_profile = {k: v for k, v in compact_profile.items() if k in keep_keys}
            report["final_columns"] = report.get("final_columns", [])[:100]
            report["final_columns_truncated"] = True

        report["insights_profile"] = compact_profile
        return report

    def _decode_correlation_matrix_for_payload(
        self,
        correlation_matrix: Any
    ) -> Dict[str, Any]:
        """
        Decode Firestore-safe matrix format into frontend-friendly square matrix:
        { columns: [...], values: [[...], ...] }
        """
        if not isinstance(correlation_matrix, dict):
            return {"columns": [], "values": []}

        columns = correlation_matrix.get("columns")
        if not isinstance(columns, list):
            columns = []

        # Legacy/non-stored format (already square matrix)
        raw_values = correlation_matrix.get("values")
        if isinstance(raw_values, list) and all(isinstance(row, list) for row in raw_values):
            max_size = min(len(columns), len(raw_values))
            values = []
            for row_idx in range(max_size):
                row = raw_values[row_idx]
                values.append([row[col_idx] if col_idx < len(row) else None for col_idx in range(max_size)])
            return {"columns": columns[:max_size], "values": values}

        # Firestore-safe storage format: rows -> [{ column, values: {col: value} }]
        raw_rows = correlation_matrix.get("rows")
        if isinstance(raw_rows, list):
            row_map: Dict[str, Dict[str, Any]] = {}
            for row in raw_rows:
                if not isinstance(row, dict):
                    continue
                row_name = row.get("column")
                row_values = row.get("values")
                if isinstance(row_name, str) and isinstance(row_values, dict):
                    row_map[row_name] = row_values

            values = []
            for row_name in columns:
                mapped_values = row_map.get(row_name, {})
                row_values = [mapped_values.get(col_name) for col_name in columns]
                values.append(row_values)

            return {"columns": columns, "values": values}

        return {"columns": columns, "values": []}

    def _build_correlation_matrix_from_pairs(
        self,
        correlation_pairs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build a square matrix from pairwise correlations (fallback for older records)."""
        if not correlation_pairs:
            return {"columns": [], "values": []}

        ordered_columns = []
        for pair in correlation_pairs:
            left = pair.get("left")
            right = pair.get("right")
            if left and left not in ordered_columns:
                ordered_columns.append(left)
            if right and right not in ordered_columns:
                ordered_columns.append(right)

        size = len(ordered_columns)
        if size == 0:
            return {"columns": [], "values": []}

        matrix = [[None for _ in range(size)] for _ in range(size)]
        for i in range(size):
            matrix[i][i] = 1.0

        column_index = {name: idx for idx, name in enumerate(ordered_columns)}
        for pair in correlation_pairs:
            left = pair.get("left")
            right = pair.get("right")
            value = pair.get("correlation")
            if left not in column_index or right not in column_index or value is None:
                continue
            i = column_index[left]
            j = column_index[right]
            matrix[i][j] = float(value)
            matrix[j][i] = float(value)

        return {
            "columns": ordered_columns,
            "values": matrix
        }
    
    def create_history_record(
        self,
        user_id: str,
        file_id: str,
        original_file_name: str,
        original_bucket_path: str,
        original_file_url: str,
        processed_file_name: Optional[str] = None,
        processed_bucket_path: Optional[str] = None,
        processed_file_url: Optional[str] = None,
        file_type: str = "csv",
        status: str = "success",
        preprocessing_report: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new history record in Firestore
        
        Args:
            user_id: Firebase user UUID
            file_id: Unique file identifier
            original_file_name: Original filename
            original_bucket_path: Path in Supabase bucket
            original_file_url: Signed URL for original file
            processed_file_name: Processed filename (None if failed)
            processed_bucket_path: Processed file path (None if failed)
            processed_file_url: Signed URL for processed file (None if failed)
            file_type: File extension (csv, xlsx, xls)
            status: Processing status (success, failed)
            preprocessing_report: Full preprocessing report
            
        Returns:
            history_id: Generated document ID
        """
        try:
            # Prepare history document
            base_history_data = {
                "user_id": user_id,
                "file_id": file_id,
                "original_file": {
                    "file_name": original_file_name,
                    "bucket_path": original_bucket_path,
                    "file_url": original_file_url
                },
                "file_type": file_type,
                "status": status,
                "created_at": firestore.SERVER_TIMESTAMP,
                "created_at_client": datetime.utcnow().isoformat() + "Z",
                "preprocessing_version": self.PREPROCESSING_VERSION
            }
            
            # Add processed file info only if successful
            if status == "success" and processed_file_name:
                base_history_data["processed_file"] = {
                    "file_name": processed_file_name,
                    "bucket_path": processed_bucket_path,
                    "file_url": processed_file_url
                }

            doc_ref = self.db.collection(self.COLLECTION_HISTORY).document()
            last_error: Optional[Exception] = None

            # Start from compact mode to reduce write size, latency, and fallback retries.
            report_modes = ["compact", "minimal"] if preprocessing_report else ["full"]

            for mode in report_modes:
                history_data = dict(base_history_data)
                if preprocessing_report:
                    history_data["preprocessing_report"] = self._compact_preprocessing_report(
                        preprocessing_report,
                        mode
                    )

                for attempt in range(1, 4):
                    try:
                        doc_ref.set(history_data)
                        history_id = doc_ref.id
                        logger.info(
                            f"Created history record: {history_id} for user: {user_id} "
                            f"(report_mode={mode}, attempt={attempt})"
                        )
                        return history_id
                    except Exception as write_err:
                        last_error = write_err
                        if attempt < 3:
                            time.sleep(0.25 * attempt)
                        else:
                            logger.warning(
                                f"History write failed (mode={mode}, attempt={attempt}): {write_err}"
                            )

                # Try next compaction mode after retries are exhausted.
                if mode != report_modes[-1]:
                    logger.warning(f"Retrying history save with more compact report mode: {mode} -> next")

            raise RuntimeError(f"Failed to create history record after retries: {last_error}")
        
        except Exception as e:
            logger.error(f"Failed to create history record: {str(e)}")
            raise RuntimeError(f"Failed to create history record: {str(e)}")
    
    def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        summary_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get preprocessing history for a specific user
        
        Args:
            user_id: Firebase user UUID
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)
            
        Returns:
            List of history records
        """
        try:
            base_query = self._where_equal(
                self.db.collection(self.COLLECTION_HISTORY),
                "user_id",
                user_id
            ).order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).offset(offset)

            query = base_query
            if summary_only:
                # Fetch only fields required for list views to reduce payload/read costs.
                query = base_query.select([
                    "original_file.file_name",
                    "processed_file.file_name",
                    "file_type",
                    "status",
                    "created_at",
                ])

            try:
                docs = query.stream()
                history = [self._normalize_history_record(doc) for doc in docs]
            except Exception:
                if not summary_only:
                    raise
                # Projection might be unsupported in some deployments; fallback to full docs.
                docs = base_query.stream()
                history = [self._normalize_history_record(doc) for doc in docs]
            
            logger.info(f"Retrieved {len(history)} history records for user: {user_id}")
            return history
        
        except Exception as e:
            logger.error(f"Failed to get user history: {str(e)}")
            raise RuntimeError(f"Failed to get user history: {str(e)}")

    def get_user_completed_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get successful preprocessing history for a specific user.
        Uses summary projection and avoids expensive full-document reads.
        """
        try:
            # Over-fetch to account for failed records, then filter in-memory.
            # This avoids requiring additional composite indexes.
            scan_limit = max(limit * 2, 100)
            records = self.get_user_history(
                user_id=user_id,
                limit=scan_limit,
                offset=offset,
                summary_only=True
            )

            completed = [r for r in records if r.get("status") == "success"]

            if len(completed) < limit and len(records) == scan_limit:
                second_batch = self.get_user_history(
                    user_id=user_id,
                    limit=scan_limit,
                    offset=offset + scan_limit,
                    summary_only=True
                )
                completed.extend(r for r in second_batch if r.get("status") == "success")

            return completed[:limit]

        except Exception as e:
            logger.error(f"Failed to get completed history: {str(e)}")
            raise RuntimeError(f"Failed to get completed history: {str(e)}")
    
    def get_history_by_id(
        self,
        history_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single history record by ID
        Ensures user can only access their own records
        
        Args:
            history_id: History document ID
            user_id: Firebase user UUID (for verification)
            
        Returns:
            History record or None if not found/unauthorized
        """
        try:
            doc_ref = self.db.collection(self.COLLECTION_HISTORY).document(history_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"History record not found: {history_id}")
                return None
            
            data = doc.to_dict()
            
            # Security check: ensure user owns this record
            if data.get("user_id") != user_id:
                logger.warning(
                    f"Unauthorized access attempt: user {user_id} "
                    f"tried to access history {history_id}"
                )
                return None
            
            return self._normalize_history_record(doc)
        
        except Exception as e:
            logger.error(f"Failed to get history by ID: {str(e)}")
            raise RuntimeError(f"Failed to get history by ID: {str(e)}")
    
    def delete_history_record(
        self,
        history_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a history record
        Ensures user can only delete their own records
        
        Args:
            history_id: History document ID
            user_id: Firebase user UUID (for verification)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # First verify ownership
            doc_ref = self.db.collection(self.COLLECTION_HISTORY).document(history_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"History record not found: {history_id}")
                return False
            
            data = doc.to_dict()
            
            # Security check
            if data.get("user_id") != user_id:
                logger.warning(
                    f"Unauthorized delete attempt: user {user_id} "
                    f"tried to delete history {history_id}"
                )
                return False
            
            # Delete the document
            doc_ref.delete()
            logger.info(f"Deleted history record: {history_id} for user: {user_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete history record: {str(e)}")
            raise RuntimeError(f"Failed to delete history record: {str(e)}")
    
    def count_user_history(self, user_id: str, status: Optional[str] = None) -> int:
        """
        Count total number of history records for a user
        
        Args:
            user_id: Firebase user UUID
            
        Returns:
            Total count
        """
        try:
            query = self._where_equal(
                self.db.collection(self.COLLECTION_HISTORY),
                "user_id",
                user_id
            )
            if status:
                query = self._where_equal(query, "status", status)

            try:
                # Aggregation query returns only the count value (lower cost and latency).
                count = int(query.count().get()[0][0].value)
            except Exception:
                # Fallback for environments where aggregation queries are unavailable.
                docs = list(query.stream())
                count = len(docs)
            
            logger.info(f"User {user_id} has {count} history records")
            return count
        
        except Exception as e:
            logger.error(f"Failed to count user history: {str(e)}")
            return 0

    def build_insights_payload(
        self,
        history_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Build lightweight insights payload from stored preprocessing report.
        This intentionally avoids reading raw files or re-running preprocessing.
        """
        record = self.get_history_by_id(history_id=history_id, user_id=user_id)
        if not record:
            return None

        report = record.get("preprocessing_report") or {}
        insights_profile = report.get("insights_profile") or {}
        original_shape = report.get("original_shape") or [0, 0]
        final_shape = report.get("final_shape") or [0, 0]
        column_types = report.get("column_types") or {}

        original_rows = int(original_shape[0]) if len(original_shape) > 0 else 0
        original_columns = int(original_shape[1]) if len(original_shape) > 1 else 0
        final_rows = int(final_shape[0]) if len(final_shape) > 0 else 0
        final_columns = int(final_shape[1]) if len(final_shape) > 1 else 0
        rows_removed = int(report.get("rows_removed") or 0)

        data_quality_score = round(
            ((final_rows / original_rows) * 100.0) if original_rows > 0 else 0.0,
            2
        )

        payload = {
            "history_id": record.get("history_id"),
            "original_file_name": (record.get("original_file") or {}).get("file_name"),
            "processed_file_name": (record.get("processed_file") or {}).get("file_name"),
            "created_at": record.get("created_at"),
            "status": record.get("status"),
            "summary": {
                "original_rows": original_rows,
                "processed_rows": final_rows,
                "original_columns": original_columns,
                "processed_columns": final_columns,
                "rows_removed": rows_removed,
                "columns_added": int(report.get("columns_added") or 0),
                "columns_dropped": len(report.get("dropped_columns") or []),
                "duplicates_removed": int(report.get("duplicates_removed") or 0),
                "features_engineered": int(report.get("features_engineered") or 0),
                "processing_time_seconds": float(report.get("processing_time_seconds") or 0.0),
                "data_quality_score": data_quality_score,
            },
            "column_type_distribution": [
                {"name": "Numerical", "value": int(column_types.get("numerical") or 0)},
                {"name": "Categorical", "value": int(column_types.get("categorical") or 0)},
                {"name": "Count", "value": int(column_types.get("count") or 0)},
                {"name": "Datetime", "value": int(column_types.get("datetime") or 0)},
                {"name": "Boolean", "value": int(column_types.get("boolean") or 0)},
                {"name": "ID", "value": int(column_types.get("id") or 0)},
            ],
            "dropped_columns": report.get("dropped_columns") or [],
            "removed_non_informative_columns": report.get("non_informative_columns_removed") or [],
            "final_columns_sample": (report.get("final_columns") or [])[:20],
            "report_timestamp": report.get("timestamp"),
        }

        # Rich profile for advanced insights UI (new records)
        if insights_profile and not insights_profile.get("error"):
            payload["profile_version"] = insights_profile.get("version", "v1")
            payload["profile_generated_at"] = insights_profile.get("generated_at")
            payload["profile_storage_mode"] = insights_profile.get("storage_mode", "full")
            payload["dataset_overview"] = insights_profile.get("dataset_overview", {})
            payload["column_details"] = insights_profile.get("column_details", [])
            payload["missing_values_by_column"] = insights_profile.get("missing_values_by_column", [])
            payload["numerical_statistics"] = insights_profile.get("numerical_statistics", [])
            payload["correlation_pairs"] = insights_profile.get("correlation_pairs", [])
            payload["correlation_matrix"] = self._decode_correlation_matrix_for_payload(
                insights_profile.get("correlation_matrix")
            )
            payload["categorical_distributions"] = insights_profile.get("categorical_distributions", [])
            payload["outlier_summary"] = insights_profile.get("outlier_summary", [])
            payload["highlights"] = insights_profile.get("highlights", [])
            payload["limits"] = insights_profile.get("limits", {})
            payload["truncated"] = insights_profile.get("truncated", {})
            payload["column_type_distribution"] = insights_profile.get("data_type_distribution", payload["column_type_distribution"])

            if (
                not payload["correlation_matrix"].get("columns")
                and payload.get("correlation_pairs")
            ):
                payload["correlation_matrix"] = self._build_correlation_matrix_from_pairs(
                    payload["correlation_pairs"]
                )

        return payload


# Singleton instance
_firestore_service: Optional[FirestoreService] = None


def get_firestore_service() -> FirestoreService:
    """Get or create Firestore service singleton"""
    global _firestore_service
    
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    
    return _firestore_service
