// src/services/userService.js
import axiosClient from "../api/axiosClient";

const userService = {
  // Lấy thông tin user (Trùng với authService.getMe, nhưng giữ lại nếu muốn tách biệt)
  getProfile: async () => {
    return axiosClient.get("/auth/me");
  },

  // Upload Avatar
  // Backend: POST /api/auth/upload-avatar
  uploadAvatar: async (file) => {
    const formData = new FormData();
    formData.append("file", file); // Key 'file' khớp với backend: request.files['file']

    return axiosClient.post("/auth/upload-avatar", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  // Cập nhật thông tin User (Tạm để dành nếu sau này bạn làm API update info)
  // updateProfile: async (data) => {
  //   return axiosClient.put("/auth/me", data);
  // }
};

export default userService;
