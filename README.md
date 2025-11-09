# ⚽ Vleague_Web

**Vleague_Web** là dự án thu thập, quản lý và phân tích dữ liệu các mùa giải **V-League** (từ mùa 2022 đến 2024/25), bao gồm cầu thủ, đội bóng, trọng tài, sân vận động và kết quả thi đấu.

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
- Thông tin cơ bản: tên đội, logo, thành phố, v.v.

---

### 🧍‍♂️ `Players`
Danh sách **toàn bộ cầu thủ** đã từng thi đấu ở V-League.  
- Chỉ lưu **thông tin sinh học**: họ tên, ngày sinh, chiều cao, cân nặng, vị trí.  
- Không lưu thông tin đội bóng hay số áo — những thông tin này sẽ được quản lý qua bảng `TeamRosters`.

---

### ⚖️ `Referees`
Danh sách **trọng tài** của V-League, bao gồm trọng tài chính, trọng tài biên, trọng tài bàn, VAR, v.v.

---

### 📋 `TeamRosters`
Bảng **đăng ký cầu thủ theo mùa giải**, trả lời câu hỏi:

> “Cầu thủ A thi đấu cho Đội B ở Mùa giải C với số áo X?”

Ví dụ:
```sql
(player_id=1, team_id=1, season_id=1, shirt_number=10)
