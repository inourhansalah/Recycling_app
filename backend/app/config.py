import os

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE_MB = 5

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES + [
    "application/pdf"
]

# Business Logic Constants
RECYCLING_REWARD_CONVERSION_RATE = 10  # 1 EGP = 10 points