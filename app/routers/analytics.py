from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import AwardsResponse, LeaderboardEntry, VolunteerSummaryResponse
from app.services.analytics_service import get_awards, get_leaderboard, get_volunteer_summary
from app.utils.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(get_current_user)])


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[LeaderboardEntry]:
    return get_leaderboard(db, limit=limit)


@router.get("/awards", response_model=AwardsResponse)
def awards(db: Session = Depends(get_db)) -> AwardsResponse:
    return get_awards(db)


@router.get("/volunteers/{volunteer_id}/summary", response_model=VolunteerSummaryResponse)
def volunteer_summary(volunteer_id: int, db: Session = Depends(get_db)) -> VolunteerSummaryResponse:
    summary = get_volunteer_summary(db, volunteer_id=volunteer_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer not found")
    return summary