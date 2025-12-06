// src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from "react";
import authService from "../services/authService";
import axiosClient from "../api/axiosClient";

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Kiểm tra đăng nhập khi khởi động app
    const token = authService.getToken();
    if (token) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authService.checkAuth();
      if (response.success) {
        const currentUser = authService.getCurrentUser();
        setUser(currentUser);
      } else {
        authService.logout();
        setUser(null);
      }
    } catch (error) {
      authService.logout();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await authService.login({ email, password });
      if (response.success) {
        const currentUser = authService.getCurrentUser();
        setUser(currentUser);
        return { success: true };
      }
      return { success: false, message: response.message };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || "Đăng nhập thất bại",
      };
    }
  };

  const googleLogin = async () => {
    try {
      // Lấy URL đăng nhập Google từ backend
      const response = await axiosClient.get("/auth/google");

      if (response.success) {
        const authUrl = response.data.auth_url;

        // Mở popup đăng nhập Google
        const width = 500;
        const height = 600;
        const left = window.screen.width / 2 - width / 2;
        const top = window.screen.height / 2 - height / 2;

        const popup = window.open(
          authUrl,
          "google_login",
          `width=${width},height=${height},left=${left},top=${top}`
        );

        // Nếu popup bị chặn
        if (!popup || popup.closed || typeof popup.closed === "undefined") {
          throw new Error(
            "Popup đăng nhập Google bị chặn. Vui lòng cho phép popup."
          );
        }

        return new Promise((resolve, reject) => {
          let timeoutId;

          // Lắng nghe message từ popup
          const messageListener = (event) => {
            if (event.origin !== window.location.origin) return;

            if (event.data.type === "GOOGLE_LOGIN_SUCCESS") {
              const { access_token, refresh_token, user } = event.data.data;

              // Lưu token và user
              localStorage.setItem("access_token", access_token);
              localStorage.setItem("refresh_token", refresh_token);
              localStorage.setItem("user", JSON.stringify(user));

              setUser(user);
              window.removeEventListener("message", messageListener);
              clearTimeout(timeoutId);
              popup?.close();

              resolve({ success: true });
            } else if (event.data.type === "GOOGLE_LOGIN_ERROR") {
              window.removeEventListener("message", messageListener);
              clearTimeout(timeoutId);
              popup?.close();

              reject({
                success: false,
                message: event.data.message || "Đăng nhập Google thất bại",
              });
            }
          };

          window.addEventListener("message", messageListener);

          // Timeout sau 60 giây
          timeoutId = setTimeout(() => {
            window.removeEventListener("message", messageListener);
            popup?.close();
            reject({
              success: false,
              message: "Đăng nhập Google timeout. Vui lòng thử lại.",
            });
          }, 60000);

          // Kiểm tra popup đóng
          const checkPopup = setInterval(() => {
            if (popup?.closed) {
              clearInterval(checkPopup);
              window.removeEventListener("message", messageListener);
              clearTimeout(timeoutId);

              // Chỉ reject nếu chưa nhận được message thành công
              if (!localStorage.getItem("access_token")) {
                reject({
                  success: false,
                  message: "Popup đã đóng trước khi hoàn tất đăng nhập",
                });
              }
            }
          }, 500);
        });
      }

      return { success: false, message: "Không thể lấy URL đăng nhập Google" };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || "Lỗi kết nối server",
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authService.register(userData);
      if (response.success) {
        const currentUser = authService.getCurrentUser();
        setUser(currentUser);
        return { success: true };
      }
      return { success: false, message: response.message };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || "Đăng ký thất bại",
      };
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    googleLogin,
    register,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
