// src/services/postService.js
import axiosClient from "../api/axiosClient";

const postService = {
  // Lấy tất cả bài viết
  getAllPosts: async (params = {}) => {
    try {
      const response = await axiosClient.get("/posts", { params });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy bài viết theo ID
  getPostById: async (postId) => {
    try {
      const response = await axiosClient.get(`/posts/${postId}`, {
        params: { include_counts: true },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Tạo bài viết mới
  createPost: async (postData) => {
    try {
      const response = await axiosClient.post("/posts", postData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Cập nhật bài viết
  updatePost: async (postId, postData) => {
    try {
      const response = await axiosClient.put(`/posts/${postId}`, postData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Xóa bài viết
  deletePost: async (postId) => {
    try {
      const response = await axiosClient.delete(`/posts/${postId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy bài viết theo user
  getPostsByUser: async (userId, include_counts = true) => {
    try {
      const response = await axiosClient.get(`/posts/user/${userId}`, {
        params: { include_counts },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy bài viết theo trận đấu
  getPostsByMatch: async (matchId) => {
    try {
      const response = await axiosClient.get(`/posts/match/${matchId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Tìm kiếm bài viết
  searchPosts: async (keyword) => {
    try {
      const response = await axiosClient.get("/posts/search", {
        params: { keyword },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy bài viết trending
  getTrendingPosts: async (limit = 10) => {
    try {
      const response = await axiosClient.get("/posts/trending", {
        params: { limit },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },
};

export default postService;
