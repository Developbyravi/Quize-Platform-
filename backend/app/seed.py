from app.core.database import SessionLocal, engine, Base
from app.utils.seed_data import seed_database
from app.models.user import User, Participant
from app.models.round import Round, RoundAttempt, CodeDraft
from app.models.question import Question, QuestionOption, TestCase
from app.models.submission import Submission, QuizAnswer
from app.models.leaderboard import Score
from app.models.violation import Violation
from app.models.setting import ContestSettings

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Seeding initial competition dataset...")
        seed_database(db)
        print("Database seeding completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
