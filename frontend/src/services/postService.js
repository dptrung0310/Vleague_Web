import axiosClient from "../api/axiosClient";

// --- 1. THÊM HÀM NÀY ĐỂ LẤY TOKEN TỪ LOCALSTORAGE ---
const authHeader = () => {
  const token = localStorage.getItem("token"); // Lấy token đã lưu khi login
  if (token) {
    // Trả về header Authorization chuẩn JWT
    return { Authorization: `Bearer ${token}` };
  }
  return {};
};

const postService = {
  // 1. Lấy danh sách bài viết (Đã thêm tham số search)
  getPosts: (page = 1, limit = 10, search = "") => {
    return axiosClient.get("/posts", {
      params: {
        page,
        limit,
        search, // Truyền từ khóa tìm kiếm lên server
      },
      headers: authHeader(), // Gọi hàm authHeader vừa khai báo ở trên
    });
  },

  // 2. Tạo bài viết mới
  createPost: (data) => {
    return axiosClient.post("/posts", data, {
      headers: {
        ...authHeader(), // Kế thừa header xác thực
        "Content-Type": "multipart/form-data",
      },
    });
  },

  // 3. Xóa bài viết
  deletePost: (postId) => {
    return axiosClient.delete(`/posts/${postId}`, {
      headers: authHeader(),
    });
  },

  // 4. Like / Unlike
  toggleLike: (postId) => {
    return axiosClient.post(
      `/posts/${postId}/like`,
      {},
      {
        headers: authHeader(),
      }
    );
  },

  // 5. Bình luận
  addComment: (postId, content) => {
    return axiosClient.post(
      `/posts/${postId}/comment`,
      { content },
      {
        headers: authHeader(),
      }
    );
  },
};

export default postService;
