// src/services/achievementService.js
import axiosClient from "../api/axiosClient";

const achievementService = {
  // Lấy tất cả thành tựu
  getAllAchievements: async () => {
    try {
      const response = await axiosClient.get("/achievements");
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy thành tựu của user
  getUserAchievements: async (userId) => {
    try {
      const response = await axiosClient.get(
        `/user-achievements/user/${userId}`
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy thành tựu của tôi
  getMyAchievements: async () => {
    try {
      const response = await axiosClient.get(
        "/user-achievements/my-achievements"
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy thành tựu mới nhất
  getRecentUnlocks: async (limit = 10) => {
    try {
      const response = await axiosClient.get("/user-achievements/recent", {
        params: { limit },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },
};

export default achievementService;
