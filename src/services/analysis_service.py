import json
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from src.database.database import AnalysisHistory
from src.models.analysis import AnalysisHistoryItem, AnalysisResponse

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Service layer for managing code analysis operations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def save_analysis(
        self, 
        db_session: AsyncSession,
        code_snippet: str,
        analysis_result: dict,
        processing_time: int
    ) -> int:
        """
        Save analysis result to database
        
        Returns:
            int: The ID of the saved analysis
        """
        try:
            # Convert suggestions to JSON string
            suggestions_json = json.dumps(analysis_result.get('suggestions', []))
            
            # Create new analysis record
            analysis_record = AnalysisHistory(
                code_snippet=code_snippet,
                suggestions=suggestions_json,
                created_at=datetime.utcnow(),
                processing_time=processing_time,
                agent_version="1.0.0"
            )
            
            db_session.add(analysis_record)
            await db_session.commit()
            await db_session.refresh(analysis_record)
            
            self.logger.info(f"Analysis saved with ID: {analysis_record.id}")
            return analysis_record.id
            
        except Exception as e:
            await db_session.rollback()
            self.logger.error(f"Error saving analysis: {e}")
            raise
    
    async def get_analysis_history(
        self,
        db_session: AsyncSession,
        limit: int = 10,
        offset: int = 0
    ) -> List[AnalysisHistoryItem]:
        """
        Get analysis history with pagination
        """
        try:
            # Query for analysis history
            stmt = (
                select(AnalysisHistory)
                .order_by(desc(AnalysisHistory.created_at))
                .limit(limit)
                .offset(offset)
            )
            
            result = await db_session.execute(stmt)
            analyses = result.scalars().all()
            
            # Convert to response models
            history_items = []
            for analysis in analyses:
                suggestions = json.loads(analysis.suggestions) if analysis.suggestions else []
                
                # Create summary from suggestions
                summary = self._create_summary(suggestions, analysis.code_snippet)
                
                history_items.append(AnalysisHistoryItem(
                    id=analysis.id,
                    code_snippet=analysis.code_snippet[:200] + "..." if len(analysis.code_snippet) > 200 else analysis.code_snippet,
                    suggestions_count=len(suggestions),
                    created_at=analysis.created_at,
                    processing_time=analysis.processing_time,
                    summary=summary
                ))
            
            return history_items
            
        except Exception as e:
            self.logger.error(f"Error fetching analysis history: {e}")
            raise
    
    async def get_analysis_by_id(
        self,
        db_session: AsyncSession,
        analysis_id: int
    ) -> Optional[dict]:
        """
        Get specific analysis by ID
        """
        try:
            stmt = select(AnalysisHistory).where(AnalysisHistory.id == analysis_id)
            result = await db_session.execute(stmt)
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                return None
            
            # Parse suggestions from JSON
            suggestions = json.loads(analysis.suggestions) if analysis.suggestions else []
            
            return {
                "id": analysis.id,
                "code_snippet": analysis.code_snippet,
                "suggestions": suggestions,
                "created_at": analysis.created_at,
                "processing_time": analysis.processing_time,
                "agent_version": analysis.agent_version
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching analysis {analysis_id}: {e}")
            raise
    
    async def get_analysis_statistics(
        self,
        db_session: AsyncSession
    ) -> dict:
        """
        Get statistics about analyses performed
        """
        try:
            # Total analyses
            total_stmt = select(func.count(AnalysisHistory.id))
            total_result = await db_session.execute(total_stmt)
            total_analyses = total_result.scalar()
            
            # Average processing time
            avg_time_stmt = select(func.avg(AnalysisHistory.processing_time))
            avg_time_result = await db_session.execute(avg_time_stmt)
            avg_processing_time = avg_time_result.scalar() or 0
            
            # Last analysis timestamp
            last_analysis_stmt = (
                select(AnalysisHistory.created_at)
                .order_by(desc(AnalysisHistory.created_at))
                .limit(1)
            )
            last_analysis_result = await db_session.execute(last_analysis_stmt)
            last_analysis = last_analysis_result.scalar()
            
            return {
                "total_analyses": total_analyses,
                "average_processing_time": round(float(avg_processing_time), 2),
                "last_analysis": last_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching analysis statistics: {e}")
            raise
    
    async def delete_old_analyses(
        self,
        db_session: AsyncSession,
        days_old: int = 30
    ) -> int:
        """
        Delete analyses older than specified days
        
        Returns:
            int: Number of analyses deleted
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Count analyses to be deleted
            count_stmt = select(func.count(AnalysisHistory.id)).where(
                AnalysisHistory.created_at < cutoff_date
            )
            count_result = await db_session.execute(count_stmt)
            count = count_result.scalar()
            
            if count > 0:
                # Delete old analyses
                from sqlalchemy import delete
                delete_stmt = delete(AnalysisHistory).where(
                    AnalysisHistory.created_at < cutoff_date
                )
                await db_session.execute(delete_stmt)
                await db_session.commit()
                
                self.logger.info(f"Deleted {count} old analyses")
            
            return count
            
        except Exception as e:
            await db_session.rollback()
            self.logger.error(f"Error deleting old analyses: {e}")
            raise
    
    def _create_summary(self, suggestions: List[dict], code_snippet: str) -> str:
        """
        Create a summary from suggestions
        """
        if not suggestions:
            return "No issues found"
        
        # Count by severity
        severity_counts = {}
        for suggestion in suggestions:
            severity = suggestion.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Create summary
        summary_parts = []
        if severity_counts.get('critical', 0) > 0:
            summary_parts.append(f"{severity_counts['critical']} critical")
        if severity_counts.get('high', 0) > 0:
            summary_parts.append(f"{severity_counts['high']} high")
        if severity_counts.get('medium', 0) > 0:
            summary_parts.append(f"{severity_counts['medium']} medium")
        if severity_counts.get('low', 0) > 0:
            summary_parts.append(f"{severity_counts['low']} low")
        
        if summary_parts:
            return f"Found issues: {', '.join(summary_parts)}"
        else:
            return f"{len(suggestions)} suggestions found"