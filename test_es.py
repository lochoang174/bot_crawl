import logging
from services.rabbitmq_client import RabbitMQClient
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
from models.face_model import FaceVector
if __name__ == "__main__":
    rabbit = RabbitMQClient()
    mock_doc = FaceVector(
    url="https://www.linkedin.com/in/vy-ho-a15062257",
    name="Loc Hoang",
    headline="Talent Acquisition Lead at HEINEKEN",
    location="Ho Chi Minh City, Vietnam",
    current_company="HEINEKEN Vietnam",
    education=None,
    vector=[],
    picture="https://media.licdn.com/dms/image/v2/D5603AQH6htfyAkJ5KA/profile-displayphoto-shrink_400_400/B56ZahfM3xGoAg-/0/1746466033819?e=1756944000&v=beta&t=9g1qYawv8QpGLUVJX7cCTymHKmw3rqJN9UJtMi1zFJs",
    )
    payload = {
        'pattern': 'create_face_vector',
        'data': mock_doc.to_dict(),
    }
    rabbit.publish_message('face_queue',payload)



