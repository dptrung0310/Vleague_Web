// src/services/authService.js
import axiosClient from "../api/axiosClient";

const authService = {
  // Đăng ký
  register: async (userData) => {
    try {
      const response = await axiosClient.post("/auth/register", userData);
      if (response.success && response.data) {
        // Lưu token và user vào localStorage
        localStorage.setItem("access_token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        localStorage.setItem("user", JSON.stringify(response.data.user));
      }
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Đăng nhập
  login: async (credentials) => {
    try {
      const response = await axiosClient.post("/auth/login", credentials);
      if (response.success && response.data) {
        // Lưu token và user vào localStorage
        localStorage.setItem("access_token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        localStorage.setItem("user", JSON.stringify(response.data.user));
      }
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Refresh token
  refreshToken: async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      const response = await axiosClient.post(
        "/auth/refresh",
        {},
        {
          headers: {
            Authorization: `Bearer ${refreshToken}`,
          },
        }
      );

      if (response.success && response.data) {
        localStorage.setItem("access_token", response.data.access_token);
      }
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Đăng xuất
  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  },

  // Kiểm tra token
  checkAuth: async () => {
    try {
      const response = await axiosClient.get("/auth/check");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy thông tin user hiện tại
  getCurrentUser: () => {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  },

  // Kiểm tra đã đăng nhập chưa
  isAuthenticated: () => {
    return !!localStorage.getItem("access_token");
  },

  // Lấy token
  getToken: () => {
    return localStorage.getItem("access_token");
  },
};

export default authService;
