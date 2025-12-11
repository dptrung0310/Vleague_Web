// src/components/Avatar.jsx
import React from "react";

const Avatar = ({ user, className }) => {
  // Cấu hình URL backend (đảm bảo đúng cổng Flask của bạn)
  const API_URL = "http://localhost:5000";

  // Link ảnh mặc định nếu user chưa có ảnh
  const defaultImg = "https://cdn-icons-png.flaticon.com/512/149/149071.png";

  const getAvatarUrl = () => {
    if (!user || !user.avatar_url) return defaultImg;

    // Trường hợp 1: Ảnh từ Google/Facebook (bắt đầu bằng http) -> Giữ nguyên
    if (user.avatar_url.startsWith("http")) {
      return user.avatar_url;
    }

    // Trường hợp 2: Ảnh upload từ Backend (bắt đầu bằng /static)
    // -> Cần nối thêm http://localhost:5000 vào trước
    // -> Cần thêm ?t=... để chống cache (ép trình duyệt tải ảnh mới nhất)
    return `${API_URL}${user.avatar_url}?t=${new Date().getTime()}`;
  };

  return (
    <img
      src={getAvatarUrl()}
      alt={user?.full_name || "User Avatar"}
      className={`rounded-full object-cover ${className || "w-10 h-10"}`}
      onError={(e) => {
        // Nếu link ảnh lỗi thì tự động chuyển về ảnh mặc định
        e.target.src = defaultImg;
      }}
    />
  );
};

export default Avatar;
