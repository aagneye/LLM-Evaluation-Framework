import json
from pathlib import Path
from app.database import SessionLocal
from app.models import Experiment, Prompt, ModelResponse, Evaluation
from app.services.model_runner import ModelRunner
from app.services.evaluation_engine import EvaluationEngine


def run_experiment_task(experiment_id: int):
    """
    Background task to run an experiment.
    Loads prompts from dataset, runs them against the model, and evaluates responses.
    """
    db = SessionLocal()
    
    try:
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            return
        
        # Update status
        experiment.status = "running"
        db.commit()
        
        # Load prompts from dataset
        prompts = load_dataset_prompts(experiment.dataset_name, db)
        
        if not prompts:
            experiment.status = "failed"
            db.commit()
            return
        
        # Initialize services
        runner = ModelRunner()
        evaluator = EvaluationEngine()
        
        # Run each prompt
        for prompt in prompts:
            # Run model
            result = runner.run_prompt(prompt.prompt_text, experiment.model_name)
            
            if result["success"]:
                # Store response
                response = ModelResponse(
                    prompt_id=prompt.id,
                    model_name=experiment.model_name,
                    response_text=result["response_text"],
                    latency=result["latency"]
                )
                db.add(response)
                db.commit()
                db.refresh(response)
                
                # Evaluate response
                eval_result = evaluator.evaluate(prompt.prompt_text, result["response_text"])
                
                if eval_result["success"]:
                    for metric, score in eval_result["scores"].items():
                        evaluation = Evaluation(
                            response_id=response.id,
                            metric=metric,
                            score=score,
                            evaluation_method="rule"
                        )
                        db.add(evaluation)
                
                db.commit()
        
        # Mark experiment as completed
        experiment.status = "completed"
        db.commit()
    
    except Exception as e:
        if experiment:
            experiment.status = "failed"
            db.commit()
        print(f"Experiment {experiment_id} failed: {str(e)}")
    
    finally:
        db.close()


def load_dataset_prompts(dataset_name: str, db):
    """
    Load prompts from a dataset file or database.
    """
    # First, try to load from database
    prompts = db.query(Prompt).filter(Prompt.dataset_name == dataset_name).all()
    
    if prompts:
        return prompts
    
    # If not in database, try to load from file
    dataset_path = Path(__file__).parent.parent.parent.parent / "prompts" / f"{dataset_name}.json"
    
    if dataset_path.exists():
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        # Create prompts in database
        prompts = []
        for item in data:
            prompt = Prompt(
                prompt_text=item.get("prompt", ""),
                category=item.get("category"),
                dataset_name=dataset_name
            )
            db.add(prompt)
            prompts.append(prompt)
        
        db.commit()
        return prompts
    
    return []
