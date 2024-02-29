from database import SessionLocal
import models


def get_completed_quests(user_id):
    db = SessionLocal()
    try:
        quest = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.finished == True).all()
        return quest
    finally:
        db.close()


async def safe_feedback(user_id, chosen_quest, rating, feedback_text):
    db = SessionLocal()
    try:
        new_feedback = models.Feedback(
            author_id=user_id,
            feedback=feedback_text,
            quest_name=chosen_quest,
            rating=rating,
        )
        db.add(new_feedback)
        db.commit()
    finally:
        db.close()
        
        
def is_completed_quest(user_id):
    db = SessionLocal()
    try:
        quest = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.finished == True).first()
        if quest:
            return True
        return False
    finally:
        db.close()
