from .player_routes import player_bp
from .referee_routes import referee_bp
from .season_routes import season_bp
from .stadium_routes import stadium_bp
from .team_routes import team_bp
from .match_routes import match_bp
from .team_roster_routes import team_roster_bp
from .season_standing_routes import season_standing_bp
from .user_routes import user_bp
from .prediction_routes import prediction_bp
from .post_routes import post_bp
from .like_routes import like_bp 
from .comment_routes import comment_bp
from .user_achievement_routes import user_achievement_bp
from .achievement_routes import achievement_bp


__all__ = [
    'player_bp', 'referee_bp', 'season_bp',
    'stadium_bp', 'team_bp', 'match_bp',
    'team_roster_bp', 'season_standing_bp','user_bp', 'prediction_bp', 
    'post_bp', 'like_bp', 'comment_bp', 'user_achievement_bp', 'achievement_bp'
]

# Dictionary để dễ truy cập
blueprints = {
    'players': player_bp,
    'referees': referee_bp,
    'seasons': season_bp,
    'stadiums': stadium_bp,
    'teams': team_bp,
    'matches': match_bp,
    'team_rosters': team_roster_bp,
    'season_standings': season_standing_bp,
    'users': user_bp,
    'predictions': prediction_bp,
    'posts': post_bp,
    'likes': like_bp,
    'comments': comment_bp,
    'user_achievements': user_achievement_bp,
    'achievements': achievement_bp
}