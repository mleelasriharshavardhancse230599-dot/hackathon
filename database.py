from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# SQLite database
engine = create_engine('sqlite:///smart_recruiter.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Candidate table
class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    job_role = Column(String)
    score = Column(Float)
    parsed = Column(String)  # JSON string

Base.metadata.create_all(engine)

# Save result
def save_result_to_db(filename, job_role, result):
    cand = Candidate(
        filename=filename,
        job_role=job_role,
        score=result["score"],
        parsed=json.dumps(result["parsed"])
    )
    session.add(cand)
    session.commit()

# Retrieve past results
def get_past_results(job_role):
    rows = session.query(Candidate).filter_by(job_role=job_role).all()
    return [
        {
            "filename": r.filename,
            "score": r.score,
            **json.loads(r.parsed)
        } for r in rows
    ]
