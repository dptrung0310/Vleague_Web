// src/components/Footer.jsx
import React from "react";
import { Link } from "react-router-dom";
import {
  Trophy,
  Facebook,
  Twitter,
  Instagram,
  Mail,
  Phone,
  MapPin,
} from "lucide-react";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const quickLinks = [
    { label: "Trang chủ", path: "/" },
    { label: "Lịch thi đấu", path: "/matches" },
    { label: "Bảng xếp hạng", path: "/standings" },
    { label: "Đội bóng", path: "/teams" },
    { label: "Cầu thủ", path: "/players" },
    { label: "Dự đoán", path: "/predictions" },
  ];

  const resources = [
    { label: "Thống kê", path: "/stats" },
    { label: "Tin tức", path: "/news" },
    { label: "FAQ", path: "/faq" },
    { label: "Liên hệ", path: "/contact" },
    { label: "Điều khoản", path: "/terms" },
    { label: "Bảo mật", path: "/privacy" },
  ];

  return (
    <footer className="bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand Column */}
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg">
                <Trophy className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">V-League Stats</h2>
                <p className="text-gray-400 text-sm">Thống kê chuyên sâu</p>
              </div>
            </div>
            <p className="text-gray-400 mb-6">
              Cung cấp thông tin, thống kê và phân tích chi tiết về V-League -
              giải bóng đá chuyên nghiệp hàng đầu Việt Nam.
            </p>
            <div className="flex gap-4">
              <a
                href="#"
                className="p-2 bg-gray-800 hover:bg-blue-600 rounded-lg transition-colors"
              >
                <Facebook className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="p-2 bg-gray-800 hover:bg-blue-400 rounded-lg transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="p-2 bg-gray-800 hover:bg-pink-600 rounded-lg transition-colors"
              >
                <Instagram className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-bold mb-6 pb-2 border-b border-gray-700">
              Liên kết nhanh
            </h3>
            <ul className="space-y-3">
              {quickLinks.map((link) => (
                <li key={link.path}>
                  <Link
                    to={link.path}
                    className="text-gray-400 hover:text-blue-400 transition-colors flex items-center gap-2"
                  >
                    <span className="w-1 h-1 bg-blue-500 rounded-full"></span>
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-lg font-bold mb-6 pb-2 border-b border-gray-700">
              Tài nguyên
            </h3>
            <ul className="space-y-3">
              {resources.map((link) => (
                <li key={link.path}>
                  <Link
                    to={link.path}
                    className="text-gray-400 hover:text-blue-400 transition-colors flex items-center gap-2"
                  >
                    <span className="w-1 h-1 bg-green-500 rounded-full"></span>
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="text-lg font-bold mb-6 pb-2 border-b border-gray-700">
              Liên hệ
            </h3>
            <ul className="space-y-4">
              <li className="flex items-center gap-3 text-gray-400">
                <MapPin className="w-5 h-5 text-blue-400" />
                <span>Hà Nội, Việt Nam</span>
              </li>
              <li className="flex items-center gap-3 text-gray-400">
                <Phone className="w-5 h-5 text-green-400" />
                <span>+84 123 456 789</span>
              </li>
              <li className="flex items-center gap-3 text-gray-400">
                <Mail className="w-5 h-5 text-yellow-400" />
                <span>info@vleague-stats.com</span>
              </li>
            </ul>
            <div className="mt-6 p-4 bg-gray-800/50 rounded-lg">
              <p className="text-sm text-gray-400 mb-2">
                Nhận thông báo mới nhất
              </p>
              <div className="flex gap-2">
                <input
                  type="email"
                  placeholder="Email của bạn"
                  className="flex-1 px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm focus:outline-none focus:border-blue-500"
                />
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-medium transition-colors">
                  Gửi
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-center md:text-left">
              <p className="text-gray-400 text-sm">
                &copy; {currentYear} V-League Stats. Tất cả quyền được bảo lưu.
              </p>
              <p className="text-gray-500 text-xs mt-1">
                Dữ liệu được cập nhật liên tục từ nguồn chính thức.
              </p>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-400">
              <Link to="/terms" className="hover:text-white transition-colors">
                Điều khoản sử dụng
              </Link>
              <Link
                to="/privacy"
                className="hover:text-white transition-colors"
              >
                Chính sách bảo mật
              </Link>
              <Link
                to="/contact"
                className="hover:text-white transition-colors"
              >
                Liên hệ hỗ trợ
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
