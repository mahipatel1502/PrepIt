"""
Preprocessing Orchestration Service
Orchestrates the preprocessing pipeline using preprocessor.py as a black box
"""
import os
import sys
import tempfile
import logging
import shutil
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path to import preprocessor
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from preprocessor import preprocess_file
except ImportError as e:
    logging.error(f"Failed to import preprocessor: {e}")
    raise

logger = logging.getLogger(__name__)


class PreprocessingOrchestrator:
    """
    Orchestrates the preprocessing pipeline
    Treats preprocessor.py as a black box - does not modify its logic
    """
    
    def __init__(self):
        """Initialize orchestrator"""
        self.temp_dir = None
    
    def _create_temp_directory(self) -> str:
        """Create temporary directory for processing"""
        self.temp_dir = tempfile.mkdtemp(prefix="prepit_")
        logger.info(f"Created temporary directory: {self.temp_dir}")
        return self.temp_dir
    
    def _cleanup_temp_directory(self) -> None:
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def _save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to temporary location
        
        Args:
            file_content: File binary content
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        temp_dir = self._create_temp_directory()
        
        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        file_path = os.path.join(temp_dir, safe_filename)
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Saved uploaded file to: {file_path}")
        return file_path
    
    def process_file(
        self,
        file_content: bytes,
        filename: str,
        target_column: Optional[str] = None,
        missing_threshold: float = 50.0,
        outlier_method: str = 'cap',
        cardinality_threshold: int = 10,
        scaling_method: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Process file using preprocessor.py
        
        Args:
            file_content: File binary content
            filename: Original filename
            target_column: Optional target column name
            missing_threshold: Threshold for dropping columns
            outlier_method: 'cap', 'remove', or 'none'
            cardinality_threshold: Threshold for encoding
            scaling_method: 'auto', 'minmax', 'standard', or 'robust'
            
        Returns:
            Dictionary containing:
                - processed_file_path: Path to processed file
                - report: Preprocessing report
                - success: Boolean indicating success
                - error: Error message if failed
        """
        input_file_path = None
        
        try:
            # Save uploaded file to temp location
            input_file_path = self._save_uploaded_file(file_content, filename)
            
            # Verify file exists
            if not os.path.exists(input_file_path):
                raise FileNotFoundError(f"Input file not found: {input_file_path}")
            
            logger.info(f"Starting preprocessing for: {filename}")
            
            # Call preprocessor.py as black box
            # This is the ONLY place where preprocessing logic is invoked
            result = preprocess_file(
                file_path=input_file_path,
                target_column=target_column,
                save_output=True,
                output_path=None,  # Let preprocessor decide output path
                missing_threshold=missing_threshold,
                outlier_method=outlier_method,
                cardinality_threshold=cardinality_threshold,
                scaling_method=scaling_method
            )
            
            # Extract results
            processed_file_path = result['report']['output_path']
            report = result['report']
            
            # Verify processed file exists
            if not os.path.exists(processed_file_path):
                raise FileNotFoundError(f"Processed file not found: {processed_file_path}")
            
            logger.info(f"Preprocessing completed successfully")
            logger.info(f"Processed file: {processed_file_path}")
            
            return {
                "success": True,
                "processed_file_path": processed_file_path,
                "report": report,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            return {
                "success": False,
                "processed_file_path": None,
                "report": None,
                "error": str(e)
            }
    
    def cleanup(self) -> None:
        """Clean up temporary files"""
        self._cleanup_temp_directory()


# Factory function
def create_preprocessor() -> PreprocessingOrchestrator:
    """Create new preprocessing orchestrator"""
    return PreprocessingOrchestrator()
