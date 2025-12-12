// src/services/authService.js
import axiosClient from "../api/axiosClient";

const authService = {
  // Đăng ký
  register: (data) => {
    return axiosClient.post("/auth/register", data);
  },

  // Đăng nhập thường (Username/Password)
  login: (data) => {
    return axiosClient.post("/auth/login", data);
  },

  // Đăng nhập Google (Gửi token Google sang backend xác thực)
  loginGoogle: (credential) => {
    return axiosClient.post("/auth/google-login", { credential });
  },

  getMe: () => {
    return axiosClient.get("/auth/me");
  },
};

export default authService;
