# Vleague_Web
# Database: 
# Seasons: Danh sách các mùa giải (2022, 2023, 2023-24, 2024-25).
# Stadiums: Danh sách 14 sân vận động, quan trọng nhất là latitude và longitude để API tính khoảng cách.
# Teams: Danh sách 17 đội bóng, mỗi đội gắn với một home_stadium_id.
# Players: Danh sách tổng của MỌI cầu thủ. Bảng này chỉ lưu thông tin sinh học (ngày sinh, cao, nặng), không lưu số áo hay đội bóng.
# Referees: Danh sách các trọng tài.
# TeamRosters (Danh sách đăng ký): Đây là bảng trả lời câu hỏi: 'Cầu thủ A chơi cho Đội B ở Mùa giải C với số áo X?'.
    Ví dụ: (player_id=1, team_id=1, season_id=1, shirt_number=10).
    Đây là cách chúng ta xử lý việc cầu thủ đổi đội hoặc đổi số áo qua các mùa giải. 
# Matches (Trận đấu): Đây là bảng trung tâm. Nó lưu lịch thi đấu, tỉ số, và trạng thái (status). Nó liên kết season_id, home_team_id, away_team_id, và stadium_id.
# MatchLineups (Đội hình trận đấu): Ghi lại 22+ cầu thủ (từ Players) đã tham gia trận này (match_id), ai đá chính (is_starter=true), và số áo thực tế họ mặc hôm đó.
# MatchEvents (Sự kiện trận đấu): Ghi lại dòng thời gian của trận đấu (match_id). Mọi thứ từ 'goal', 'yellow_card', đều được lưu ở đây, gắn với player_id và minute.
# MatchReferees (Tổ trọng tài): Ghi lại ai (referee_id) đã làm vai trò gì (role - Trọng tài chính, VAR) trong trận đấu (match_id) này.
# SeasonStandings (Bảng xếp hạng): tính điểm, thắng, thua, hiệu số, INSERT từng hàng (1 hàng là 1 đội) vào SeasonStandings cho mỗi vòng đấu.
# Lợi ích: Khi API được gọi, nó chỉ cần đọc 14 dòng này (cực nhanh), thay vì phải tính toán lại từ 200 trận đấu (cực chậm).
