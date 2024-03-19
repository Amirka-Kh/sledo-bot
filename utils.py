import os

from database import SessionLocal
import models
# import cv2


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


# async def calculate_similarity(local_image_path, message):
#     local_image = cv2.imread(local_image_path)
#     photo = await message.photo[-1].download()
#     received_image = cv2.imread(photo)
#     gray_image1 = cv2.cvtColor(local_image, cv2.COLOR_BGR2GRAY)
#     gray_image2 = cv2.cvtColor(received_image, cv2.COLOR_BGR2GRAY)
#     ssim = cv2.compareSSIM(gray_image1, gray_image2)
#     os.remove(photo)
#     return await ssim
