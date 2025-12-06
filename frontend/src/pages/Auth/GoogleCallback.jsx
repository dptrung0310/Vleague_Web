// src/pages/Auth/GoogleCallback.jsx
import React, { useEffect, useRef } from "react";
import axiosClient from "../../api/axiosClient";

const GoogleCallback = () => {
  const [status, setStatus] = useState("Đang xử lý...");
  const hasProcessed = useRef(false); // Flag để ngăn xử lý nhiều lần

  useEffect(() => {
    const handleGoogleCallback = async () => {
      // Ngăn xử lý nhiều lần
      if (hasProcessed.current) return;
      hasProcessed.current = true;

      try {
        // Lấy code từ URL
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get("code");
        const errorParam = urlParams.get("error");

        console.log("GoogleCallback Debug:", {
          code: code ? `${code.substring(0, 20)}...` : "No code",
          error: errorParam,
          fullUrl: window.location.href,
        });

        if (errorParam) {
          throw new Error(`Lỗi từ Google: ${errorParam}`);
        }

        if (!code) {
          throw new Error("Không tìm thấy mã xác thực từ Google");
        }

        setStatus("Đang xác thực với server...");

        // Gửi code lên backend - CHỈ MỘT LẦN
        const response = await axiosClient.post("/auth/google/callback", {
          code,
        });

        console.log("Backend response:", response);

        if (response.success) {
          const { access_token, refresh_token, user } = response.data;

          setStatus("Đăng nhập thành công! Đang chuyển hướng...");

          // Gửi message về window opener
          if (window.opener) {
            window.opener.postMessage(
              {
                type: "GOOGLE_LOGIN_SUCCESS",
                data: { access_token, refresh_token, user },
              },
              window.location.origin
            );

            // Đóng popup sau 1 giây
            setTimeout(() => {
              window.close();
            }, 1000);
          } else {
            // Nếu không có popup, tự redirect
            localStorage.setItem("access_token", access_token);
            localStorage.setItem("refresh_token", refresh_token);
            localStorage.setItem("user", JSON.stringify(user));

            setTimeout(() => {
              window.location.href = "/";
            }, 2000);
          }
        } else {
          throw new Error(response.message);
        }
      } catch (error) {
        console.error("Google callback error:", error);
        setStatus(`Lỗi: ${error.message}`);

        if (window.opener) {
          window.opener.postMessage(
            {
              type: "GOOGLE_LOGIN_ERROR",
              message: error.message,
            },
            window.location.origin
          );
        }

        // Hiển thị lỗi trong 5 giây rồi đóng
        setTimeout(() => {
          window.close();
        }, 5000);
      }
    };

    handleGoogleCallback();
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-gray-100">
      <div className="max-w-md w-full text-center bg-white p-8 rounded-2xl shadow-xl">
        {status.includes("Lỗi") ? (
          <>
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              Đã xảy ra lỗi
            </h3>
            <p className="text-gray-600 mb-6">{status}</p>
            <p className="text-sm text-gray-500">
              Cửa sổ sẽ tự động đóng sau 5 giây...
            </p>
          </>
        ) : (
          <>
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              {status.includes("thành công") ? "🎉 Thành công!" : "Đang xử lý"}
            </h3>
            <p className="text-gray-600">{status}</p>
          </>
        )}
      </div>
    </div>
  );
};

export default GoogleCallback;
