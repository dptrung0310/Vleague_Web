from marshmallow import Schema, fields, validate
from datetime import datetime

class MatchSchema(Schema):
    match_id = fields.Int(dump_only=True)
    season_id = fields.Int(required=True)
    round = fields.Str()
    match_datetime = fields.DateTime(required=True)
    home_team_id = fields.Int(required=True)
    away_team_id = fields.Int(required=True)
    home_score = fields.Int()
    away_score = fields.Int()
    status = fields.Str(validate=validate.OneOf(['scheduled', 'ongoing', 'finished', 'postponed', 'cancelled']))
    stadium_id = fields.Int(required=True)
    match_url = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class MatchRefereeSchema(Schema):
    match_referee_id = fields.Int(dump_only=True)
    match_id = fields.Int(required=True)
    referee_id = fields.Int(required=True)
    role = fields.Str(required=True, validate=validate.OneOf(['main_referee', 'assistant_referee_1', 'assistant_referee_2', 'fourth_official', 'var_referee']))

class MatchLineupSchema(Schema):
    lineup_id = fields.Int(dump_only=True)
    match_id = fields.Int(required=True)
    team_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    is_starter = fields.Bool(required=True)
    shirt_number = fields.Int(required=True)
    position = fields.Str(validate=validate.OneOf(['GK', 'DF', 'MF', 'FW', 'SUB']))

class MatchEventSchema(Schema):
    event_id = fields.Int(dump_only=True)
    match_id = fields.Int(required=True)
    team_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    event_type = fields.Str(required=True, validate=validate.OneOf(['goal', 'yellow_card', 'red_card', 'substitution', 'penalty', 'own_goal', 'missed_penalty']))
    minute = fields.Int(required=True)