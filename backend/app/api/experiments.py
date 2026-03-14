from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Experiment
from app.schemas.evaluation_schema import ExperimentCreate, ExperimentResponse
from app.workers.tasks import run_experiment_task

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("/", response_model=List[ExperimentResponse])
def get_experiments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all experiments."""
    experiments = db.query(Experiment).offset(skip).limit(limit).all()
    return experiments


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """Get a specific experiment by ID."""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.post("/run", response_model=ExperimentResponse)
def run_experiment(
    experiment: ExperimentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create and run a new experiment.
    The experiment runs asynchronously in the background.
    """
    db_experiment = Experiment(**experiment.model_dump(), status="pending")
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    
    # Queue the experiment for execution
    background_tasks.add_task(run_experiment_task, db_experiment.id)
    
    return db_experiment
