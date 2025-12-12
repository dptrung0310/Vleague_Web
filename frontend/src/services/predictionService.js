import axiosClient from "../api/axiosClient";

const predictionService = {
  // Lấy danh sách TẤT CẢ trận sắp diễn ra để dự đoán (không phân trang)
  getUpcomingMatches: () => {
    return axiosClient.get("/predictions/upcoming");
  },

  // Tạo dự đoán mới
  createPrediction: async (data) => {
    console.log("Calling create prediction API with data:", data);
    try {
      const response = await axiosClient.post("/predictions", data);
      console.log("Create prediction response:", response);
      return response;
    } catch (error) {
      console.error("Create prediction error:", error);
      throw error;
    }
  },

  // Cập nhật dự đoán
  updatePrediction: async (predictionId, data) => {
    console.log(
      "Calling update API for prediction:",
      predictionId,
      "with data:",
      data
    );
    try {
      const response = await axiosClient.put(
        `/predictions/${predictionId}`,
        data
      );
      console.log("Update prediction response:", response);
      return response;
    } catch (error) {
      console.error("Update prediction error:", error);
      throw error;
    }
  },

  // Xóa dự đoán
  deletePrediction: async (predictionId) => {
    console.log(`🗑️ Calling delete API for prediction ID: ${predictionId}`);
    try {
      const response = await axiosClient.delete(`/predictions/${predictionId}`);
      console.log("✅ Delete prediction response:", response);
      return response;
    } catch (error) {
      console.error("❌ Delete prediction error:", error);
      console.error("❌ Error details:", {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
      });
      throw error;
    }
  },

  // Lấy dự đoán của người dùng
  getUserPredictions: (params = {}) => {
    return axiosClient.get("/predictions/user", { params });
  },

  // Kiểm tra xem đã dự đoán trận này chưa
  checkUserPrediction: (matchId) => {
    return axiosClient.get(`/predictions/check/${matchId}`);
  },

  // Lấy dự đoán cho một trận đấu (public)
  getMatchPredictions: (matchId) => {
    return axiosClient.get(`/predictions/match/${matchId}`);
  },
};

export default predictionService;
