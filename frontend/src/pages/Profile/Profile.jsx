import React, { useState, useEffect } from "react";
// Đảm bảo import đúng service bạn đang dùng
import userService from "../../services/userService";
import Avatar from "../../components/Avatar";

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ type: "", content: "" });

  // --- KHU VỰC 1: KHAI BÁO CÁC HÀM (Phải để ở ngoài useEffect) ---

  // Hàm tải thông tin user
  const loadUserProfile = async () => {
    try {
      // Gọi API lấy profile mới nhất
      const res = await userService.getProfile();

      // Kiểm tra dữ liệu trả về (cấu trúc có thể là res.data hoặc res)
      if (res && (res.data || res.status === "success")) {
        const userData = res.data || res;
        setUser(userData);

        // Cập nhật localStorage để Navbar tự đổi ảnh
        localStorage.setItem("user", JSON.stringify(userData));

        // Bắn sự kiện để các component khác biết data đã thay đổi
        window.dispatchEvent(new Event("storage"));
      }
    } catch (error) {
      console.error("Lỗi tải profile:", error);
      // Nếu lỗi API thì lấy tạm từ localStorage
      const savedUser = localStorage.getItem("user");
      if (savedUser) setUser(JSON.parse(savedUser));
    }
  };

  // Hàm xử lý khi chọn file
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate loại file
    if (!file.type.match("image.*")) {
      setMsg({ type: "error", content: "Chỉ chấp nhận file ảnh!" });
      return;
    }

    setLoading(true);
    setMsg({ type: "", content: "" });

    try {
      // 1. Gọi API Upload
      const res = await userService.uploadAvatar(file);

      // 2. Kiểm tra kết quả
      // Vì axiosClient đã trả về response.data, nên ta check thẳng res.status
      if (res && res.status === "success") {
        setMsg({ type: "success", content: "Cập nhật ảnh thành công!" });

        // 3. Gọi lại hàm loadUserProfile để refresh giao diện
        // (Lúc này hàm đã được định nghĩa ở trên nên sẽ không bị lỗi)
        await loadUserProfile();
      } else {
        setMsg({ type: "error", content: "Upload thất bại" });
      }
    } catch (error) {
      console.error(error);
      const errorMessage = error.response?.data?.message || "Lỗi upload ảnh";
      setMsg({ type: "error", content: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  // --- KHU VỰC 2: USE EFFECT ---

  useEffect(() => {
    // Chỉ gọi hàm khi component vừa load xong
    loadUserProfile();
  }, []);

  // --- KHU VỰC 3: GIAO DIỆN ---

  if (!user)
    return <div className="p-10 text-center">Đang tải thông tin...</div>;

  return (
    <div className="container mx-auto p-4 md:p-8 max-w-3xl">
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Header màu */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 h-32"></div>

        <div className="px-8 pb-8">
          {/* Avatar Section */}
          <div className="relative -mt-16 mb-6 flex flex-col items-center">
            <div className="relative group w-32 h-32">
              {/* Hiển thị Avatar */}
              <div className="w-32 h-32 rounded-full border-4 border-white shadow-md overflow-hidden bg-gray-200">
                <Avatar user={user} className="w-full h-full object-cover" />
              </div>

              {/* Overlay nút Upload */}
              <label className="absolute inset-0 flex flex-col items-center justify-center bg-black bg-opacity-40 rounded-full opacity-0 group-hover:opacity-100 cursor-pointer transition-all duration-300">
                <span className="text-white text-xs font-bold">Đổi ảnh</span>
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleFileChange}
                  disabled={loading}
                />
              </label>
            </div>

            {loading && (
              <p className="text-blue-600 mt-2 text-sm animate-pulse">
                Đang tải lên...
              </p>
            )}

            {msg.content && (
              <p
                className={`mt-2 text-sm font-medium ${
                  msg.type === "error" ? "text-red-500" : "text-green-600"
                }`}
              >
                {msg.content}
              </p>
            )}

            <h2 className="mt-4 text-2xl font-bold text-gray-800">
              {user.full_name || user.username}
            </h2>
            <p className="text-gray-500">{user.email}</p>
          </div>

          <hr className="border-gray-200 my-6" />

          {/* Form thông tin */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tên hiển thị
              </label>
              <input
                type="text"
                value={user.full_name || ""}
                readOnly
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="text"
                value={user.email || ""}
                readOnly
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
