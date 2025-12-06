// src/services/userService.js
import axiosClient from "../api/axiosClient";

const userService = {
  // Lấy thông tin user hiện tại
  getProfile: async () => {
    try {
      const response = await axiosClient.get("/users/me");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Cập nhật thông tin user
  updateProfile: async (userData) => {
    try {
      const response = await axiosClient.put("/users/me", userData);

      // Cập nhật user trong localStorage
      if (response.success && response.data) {
        localStorage.setItem("user", JSON.stringify(response.data));
      }

      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy thống kê cá nhân
  getStats: async () => {
    try {
      const response = await axiosClient.get("/users/me/stats");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy thông tin user khác
  getUserById: async (userId) => {
    try {
      const response = await axiosClient.get(`/users/${userId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy danh sách users
  getUsers: async (limit = 20, offset = 0) => {
    try {
      const response = await axiosClient.get("/users", {
        params: { limit, offset },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy bảng xếp hạng
  getLeaderboard: async (limit = 20) => {
    try {
      const response = await axiosClient.get("/users/leaderboard", {
        params: { limit },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Tìm kiếm user
  searchUsers: async (query, limit = 10) => {
    try {
      const response = await axiosClient.get("/users/search", {
        params: { q: query, limit },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },
};

export default userService;
