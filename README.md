# ⚽ Vleague_Web

**Vleague_Web** là dự án thu thập, quản lý và phân tích dữ liệu các mùa giải **V-League**, bao gồm cầu thủ, đội bóng, trọng tài, sân vận động và kết quả thi đấu.

---

## 🗄️ Cấu trúc cơ sở dữ liệu

### 🏆 `Seasons`
Lưu danh sách các **mùa giải**:
- Ví dụ: `2022`, `2023`, `2023-24`, `2024-25`.

---

### 🏟️ `Stadiums`
Danh sách **14 sân vận động**.
- Thuộc tính quan trọng: `latitude`, `longitude` (phục vụ API tính khoảng cách di chuyển).
- Mỗi đội bóng sẽ có một sân nhà (`home_stadium_id`).

---

### 🏳️ `Teams`
Danh sách **17 đội bóng** tham dự qua các mùa giải.  
- Mỗi đội có một **sân nhà** (liên kết đến `Stadiums`).
- Thông tin cơ bản: tên đội, home_stadium_id v.v.

---

### 🧍‍♂️ `Players`
Danh sách **toàn bộ cầu thủ** đã từng thi đấu ở V-League.  
- Chỉ lưu **thông tin sinh học**: họ tên, ngày sinh, chiều cao, cân nặng, vị trí.  
- Không lưu thông tin đội bóng hay số áo — những thông tin này sẽ được quản lý qua bảng `TeamRosters`.

---

### ⚖️ `Referees`
Danh sách **trọng tài** của V-League, bao gồm trọng tài chính, trọng tài biên, VAR, v.v.

---

### 📋 `TeamRosters`
Bảng **đăng ký cầu thủ theo mùa giải**, trả lời câu hỏi:

> “Cầu thủ A thi đấu cho Đội B ở Mùa giải C với số áo X?”

---

### ⚽ `Matches` — Trận đấu  
Đây là **bảng trung tâm** của toàn bộ cơ sở dữ liệu.  
Lưu thông tin lịch thi đấu, tỷ số và trạng thái trận đấu.

**Các cột chính:**
- `match_id` — khóa chính  
- `season_id` — liên kết đến mùa giải
- `round` - vòng đấu
- `match_datetime` - Thời gian diễn ra 
- `home_team_id`, `away_team_id` — đội chủ nhà và đội khách  
- `stadium_id` — sân thi đấu  
- `home_score`, `away_score` — tỉ số cuối cùng
- `status` — trạng thái trận đấu (`scheduled`, `live`, `finished`, `postponed`)
- `match_url` - link dẫn đến kết quả trận đấu
---

### 🧾 `MatchLineups` — Đội hình ra sân  
Ghi lại **22+ cầu thủ** đã tham gia trong một trận đấu.  

**Các cột chính:**
- `match_id` — liên kết đến bảng `Matches`  
- `player_id` — liên kết đến bảng `Players`  
- `team_id` — đội bóng của cầu thủ trong trận  
- `shirt_number` — số áo thực tế mặc trong trận  
- `is_starter` — `TRUE` nếu cầu thủ đá chính, `FALSE` nếu vào sân thay người
- `position` - vị trí chơi 

👉 Cần thiết để tái hiện lại đội hình xuất phát và danh sách dự bị của từng trận.

---

### 🎬 `MatchEvents` — Dòng thời gian sự kiện  
Ghi lại **các sự kiện diễn ra trong trận đấu**, ví dụ: bàn thắng, thẻ vàng, thay người.

**Các cột chính:**
- `event_id` — khóa chính  
- `match_id` — trận đấu liên quan
- `team_id` - đội thực hiện sự kiện  
- `player_id` — cầu thủ tham gia sự kiện  
- `minute` — phút xảy ra sự kiện  
- `event_type` — loại sự kiện (`goal`, `yellow_card`, `red_card`)  

---

### 👨‍⚖️ `MatchReferees` — Tổ trọng tài  
Ghi lại **các trọng tài tham gia điều hành** trong mỗi trận đấu.

**Các cột chính:**
- `match_id` — liên kết đến bảng `Matches`  
- `referee_id` — liên kết đến bảng `Referees`  
- `role` — vai trò cụ thể (`Trọng tài chính`, `Trợ lý 1`, `Trợ lý 2`, `Trọng tài thứ 4 (giơ bảng)`, `VAR`, `AVAR`, …)

👉 Cho phép thống kê và phân tích tần suất bắt chính, số trận điều hành của từng trọng tài.

---

### 📊 `SeasonStandings` — Bảng xếp hạng mùa giải  
Lưu bảng **xếp hạng theo từng vòng đấu**, giúp truy vấn nhanh mà không phải tính toán lại từ đầu.

**Các cột chính:**
- `season_id` — mùa giải  
- `team_id` — đội bóng  
- `round` — vòng đấu hiện tại  
- `position` — thứ hạng
- `played` - số trận đã chơi
- `points`, `wins`, `draws`, `losses` — số điểm và kết quả  
- `goals_for`, `goals_against`, `goal_difference` — thống kê bàn thắng/thua  

> 💡 **Lợi ích:** Khi API cần hiển thị bảng xếp hạng, chỉ cần đọc 14 dòng (mỗi đội 1 dòng) thay vì phải tính toán lại toàn bộ 200+ trận đấu → **truy vấn cực nhanh**.

---

