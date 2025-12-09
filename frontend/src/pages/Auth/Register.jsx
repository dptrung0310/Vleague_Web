import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import authService from "../../services/authService";

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    full_name: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleRegister = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword)
      return setError("Mật khẩu không khớp");

    setLoading(true);
    try {
      const res = await authService.register(formData);
      // Đăng ký xong tự login luôn
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      navigate("/");
      window.location.reload();
    } catch (err) {
      setError(err.response?.data?.message || "Đăng ký thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-lg space-y-6">
        <h2 className="text-center text-3xl font-extrabold text-gray-900">
          Đăng ký tài khoản
        </h2>
        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded text-sm text-center">
            {error}
          </div>
        )}

        <form className="space-y-4" onSubmit={handleRegister}>
          <input
            name="full_name"
            type="text"
            required
            className="w-full px-3 py-2 border rounded"
            placeholder="Họ và tên"
            onChange={handleChange}
          />
          <input
            name="username"
            type="text"
            required
            className="w-full px-3 py-2 border rounded"
            placeholder="Tên đăng nhập (Username)"
            onChange={handleChange}
          />
          <input
            name="email"
            type="email"
            required
            className="w-full px-3 py-2 border rounded"
            placeholder="Email"
            onChange={handleChange}
          />
          <input
            name="password"
            type="password"
            required
            className="w-full px-3 py-2 border rounded"
            placeholder="Mật khẩu"
            onChange={handleChange}
          />
          <input
            name="confirmPassword"
            type="password"
            required
            className="w-full px-3 py-2 border rounded"
            placeholder="Nhập lại mật khẩu"
            onChange={handleChange}
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 border border-transparent rounded-md text-white bg-blue-600 hover:bg-blue-700 font-medium"
          >
            {loading ? "Đang tạo tài khoản..." : "Đăng ký"}
          </button>
        </form>
        <div className="text-center">
          <Link to="/login" className="text-blue-600 hover:underline text-sm">
            Đã có tài khoản? Đăng nhập
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
