// src/components/Navbar.jsx
import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import Avatar from "./Avatar"; // Đảm bảo đã có file này

const Navbar = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Kiểm tra xem có user trong kho lưu trữ không
    const userStr = localStorage.getItem("user");
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
  }, []);

  const handleLogout = () => {
    // Xóa token và thông tin user
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    // Cập nhật giao diện ngay lập tức
    setUser(null);
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4 flex justify-between items-center h-16">
        <Link
          to="/"
          className="text-2xl font-bold text-blue-800 flex items-center gap-2"
        >
          ⚽ V-League
        </Link>

        {/* Menu Desktop */}
        <div className="hidden md:flex space-x-6 font-medium">
          <Link to="/" className="text-gray-700 hover:text-blue-600 transition">
            Trang chủ
          </Link>
          <Link
            to="/teams"
            className="text-gray-700 hover:text-blue-600 transition"
          >
            Đội bóng
          </Link>
          <Link
            to="/players"
            className="text-gray-700 hover:text-blue-600 transition"
          >
            Cầu thủ
          </Link>
          <Link to="/" className="text-gray-700 hover:text-blue-600 transition">
            Dự đoán
          </Link>
          <Link
            to="/feed"
            className="text-gray-700 hover:text-blue-600 transition font-semibold"
          >
            Bảng tin
          </Link>
        </div>

        {/* Khu vực User */}
        <div>
          {user ? (
            <div className="flex items-center gap-3">
              {/* Bọc tên và avatar trong Link trỏ về /profile */}
              <Link
                to="/profile"
                className="flex items-center gap-2 group cursor-pointer"
              >
                <span className="font-semibold text-gray-700 hidden md:block group-hover:text-blue-600 transition">
                  {user.full_name || user.username}
                </span>

                {/* Component Avatar */}
                <div className="group-hover:ring-2 ring-blue-500 rounded-full transition">
                  {user && <Avatar user={user} />}
                </div>
              </Link>

              <button
                onClick={handleLogout}
                className="text-sm font-medium text-red-500 hover:text-red-700 ml-2 border-l pl-3 border-gray-300"
              >
                Đăng xuất
              </button>
            </div>
          ) : (
            <div className="flex gap-3">
              <Link
                to="/login"
                className="text-blue-600 font-bold hover:bg-blue-50 px-4 py-2 rounded-lg transition"
              >
                Đăng nhập
              </Link>
              <Link
                to="/register"
                className="bg-blue-600 text-white font-bold px-4 py-2 rounded-lg hover:bg-blue-700 transition shadow-md shadow-blue-500/30"
              >
                Đăng ký
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
