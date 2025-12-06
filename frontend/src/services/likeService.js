// src/services/likeService.js
import axiosClient from "../api/axiosClient";

const likeService = {
  // Like bài viết
  likePost: async (postId) => {
    try {
      const response = await axiosClient.post("/likes", { post_id: postId });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Bỏ like bài viết
  unlikePost: async (postId) => {
    try {
      const response = await axiosClient.delete("/likes/unlike", {
        data: { post_id: postId },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Kiểm tra đã like chưa
  checkLike: async (postId) => {
    try {
      const response = await axiosClient.get("/likes/check", {
        params: { post_id: postId },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy lượt like theo bài viết
  getLikesByPost: async (postId) => {
    try {
      const response = await axiosClient.get(`/likes/post/${postId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy số lượt like
  getLikeCount: async (postId) => {
    try {
      const response = await axiosClient.get(`/likes/count/${postId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },
};

export default likeService;
