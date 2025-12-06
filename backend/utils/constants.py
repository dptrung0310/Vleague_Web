# utils/constants.py

# User roles
USER_ROLES = {
    'USER': 'user',
    'ADMIN': 'admin',
    'MODERATOR': 'moderator'
}

# Post types
POST_TYPES = {
    'GENERAL': 'GENERAL',
    'MATCH_REVIEW': 'MATCH_REVIEW',
    'PREDICTION': 'PREDICTION',
    'NEWS': 'NEWS',
    'ANALYSIS': 'ANALYSIS'
}

# Match statuses
MATCH_STATUSES = {
    'UPCOMING': 'UPCOMING',
    'LIVE': 'LIVE',
    'FINISHED': 'FINISHED',
    'POSTPONED': 'POSTPONED',
    'CANCELLED': 'CANCELLED'
}

# Prediction results
PREDICTION_RESULTS = {
    'HOME_WIN': 'HOME_WIN',
    'DRAW': 'DRAW',
    'AWAY_WIN': 'AWAY_WIN'
}

# Prediction statuses
PREDICTION_STATUSES = {
    'PENDING': 'PENDING',
    'CORRECT': 'CORRECT',
    'INCORRECT': 'INCORRECT',
    'PROCESSED': 'PROCESSED'
}

# Achievement types
ACHIEVEMENT_TYPES = {
    'TOTAL_POINTS': 'TOTAL_POINTS',
    'CORRECT_STREAK': 'CORRECT_STREAK',
    'PERFECT_PREDICTION': 'PERFECT_PREDICTION',
    'FIRST_PREDICTION': 'FIRST_PREDICTION',
    'COMMUNITY_CONTRIBUTOR': 'COMMUNITY_CONTRIBUTOR',
    'POST_MILESTONE': 'POST_MILESTONE'
}

# Error messages
ERROR_MESSAGES = {
    'UNAUTHORIZED': 'Unauthorized access',
    'FORBIDDEN': 'Forbidden',
    'NOT_FOUND': 'Resource not found',
    'VALIDATION_ERROR': 'Validation error',
    'DATABASE_ERROR': 'Database error',
    'SERVER_ERROR': 'Internal server error'
}

# Success messages
SUCCESS_MESSAGES = {
    'CREATED': 'Created successfully',
    'UPDATED': 'Updated successfully',
    'DELETED': 'Deleted successfully',
    'LOGIN': 'Login successful',
    'REGISTER': 'Registration successful',
    'LOGOUT': 'Logout successful'
}

# Points system
POINTS_SYSTEM = {
    'CORRECT_RESULT': 10,  # Đoán đúng kết quả (1x2)
    'CORRECT_SCORE': 25,   # Đoán đúng tỉ số chính xác
    'POST_CREATED': 5,     # Tạo bài viết
    'COMMENT_CREATED': 2,  # Tạo bình luận
    'LIKE_RECEIVED': 1,    # Nhận được like
    'ACHIEVEMENT_UNLOCKED': 50  # Mở khóa thành tựu
}

# API response format
API_RESPONSE_FORMAT = {
    'success': True,
    'message': '',
    'data': None,
    'errors': [],
    'pagination': None
}