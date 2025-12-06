// src/services/commentService.js
import axiosClient from "../api/axiosClient";

const commentService = {
  // Lấy bình luận theo bài viết
  getCommentsByPost: async (postId) => {
    try {
      const response = await axiosClient.get(`/comments/post/${postId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Tạo bình luận mới
  createComment: async (commentData) => {
    try {
      const response = await axiosClient.post("/comments", commentData);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Cập nhật bình luận
  updateComment: async (commentId, commentData) => {
    try {
      const response = await axiosClient.put(
        `/comments/${commentId}`,
        commentData
      );
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Xóa bình luận
  deleteComment: async (commentId) => {
    try {
      const response = await axiosClient.delete(`/comments/${commentId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  // Lấy số bình luận
  getCommentCount: async (postId) => {
    try {
      const response = await axiosClient.get(`/comments/count/${postId}`);
      return response;
    } catch (error) {
      throw error;
    }
  },
};

export default commentService;
