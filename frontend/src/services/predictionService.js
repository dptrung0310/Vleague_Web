// src/services/predictionService.js
import axiosClient from "../api/axiosClient";

const predictionService = {
  // Tạo dự đoán mới
  createPrediction: async (predictionData) => {
    try {
      const response = await axiosClient.post("/predictions", predictionData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy dự đoán theo user
  getPredictionsByUser: async (userId) => {
    try {
      const response = await axiosClient.get(`/predictions/user/${userId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy dự đoán theo trận đấu
  getPredictionsByMatch: async (matchId) => {
    try {
      const response = await axiosClient.get(`/predictions/match/${matchId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy dự đoán của tôi
  getMyPredictions: async () => {
    try {
      const user = JSON.parse(localStorage.getItem("user"));
      if (!user) throw new Error("User not found");

      const response = await axiosClient.get(
        `/predictions/user/${user.user_id}`
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Cập nhật dự đoán
  updatePrediction: async (predictionId, predictionData) => {
    try {
      const response = await axiosClient.put(
        `/predictions/${predictionId}`,
        predictionData
      );
      return response;
    } catch (error) {
      throw error;
    }
  },
};

export default predictionService;
