// src/components/MatchPost.jsx
import React from "react";
import { Calendar, MapPin, Trophy } from "lucide-react";

const MatchPost = ({ match, onClick }) => {
  // Format ngày tháng: giờ:phút - ngày/tháng
  const formatDate = (dateString) => {
    if (!dateString) return "Chưa có lịch";
    const date = new Date(dateString);

    const time = `${String(date.getHours()).padStart(2, "0")}:${String(
      date.getMinutes()
    ).padStart(2, "0")}`;
    const day = `${String(date.getDate()).padStart(2, "0")}/${String(
      date.getMonth() + 1
    ).padStart(2, "0")}`;

    return (
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <Calendar className="w-4 h-4" />
        <span>{time}</span>
        <span className="text-gray-400">•</span>
        <span>{day}</span>
      </div>
    );
  };

  // Helper hiển thị logo
  const renderLogo = (logoUrl, teamName) => {
    if (logoUrl) {
      return (
        <div className="relative group">
          <img
            src={logoUrl}
            alt={`Logo ${teamName}`}
            className="w-20 h-20 object-contain drop-shadow-md transition-transform group-hover:scale-110"
            onError={(e) => {
              e.target.style.display = "none";
              e.target.nextSibling.style.display = "flex";
            }}
          />
          <div className="absolute inset-0 hidden items-center justify-center">
            <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center border-2 border-gray-300">
              <span className="text-lg font-bold text-gray-600">
                {teamName?.charAt(0) || "T"}
              </span>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center border-2 border-gray-300">
        <span className="text-xl font-bold text-gray-600">
          {teamName?.charAt(0) || "T"}
        </span>
      </div>
    );
  };

  return (
    <div
      className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-200 cursor-pointer group"
      onClick={() => onClick(match)}
    >
      {/* Header với giải đấu */}
      <div className="bg-gradient-to-r from-gray-50 to-white px-6 py-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg">
              <Trophy className="w-5 h-5 text-white" />
            </div>
            <h3 className="font-bold text-gray-900 text-base">
              {match.season_name || "V-League"}
            </h3>
          </div>
          {formatDate(match.match_datetime)}
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
            {match.round}
          </span>
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <MapPin className="w-4 h-4" />
            <span>{match.stadium_name || "Sân vận động"}</span>
          </div>
        </div>
      </div>

      {/* Nội dung trận đấu */}
      <div className="p-6">
        <div className="grid grid-cols-3 items-center">
          {/* Đội nhà */}
          <div className="flex flex-col items-center text-center">
            {renderLogo(match.home_team?.logo_url, match.home_team?.name)}
            <div className="mt-4">
              <h4 className="font-bold text-gray-900 text-base md:text-lg leading-tight line-clamp-2">
                {match.home_team?.name || `Đội ${match.home_team_id}`}
              </h4>
            </div>
          </div>

          {/* Tỷ số */}
          <div className="flex flex-col items-center">
            {match.status === "Kết thúc" ? (
              <>
                <div className="text-5xl md:text-6xl font-black text-gray-900 tracking-tight mb-2">
                  {match.home_score || 0}
                  <span className="mx-2 text-gray-400">-</span>
                  {match.away_score || 0}
                </div>
                <div className="px-5 py-1.5 rounded-full bg-green-100 text-green-800 text-xs font-semibold border border-green-200">
                  {match.status}
                </div>
              </>
            ) : (
              <>
                <div className="text-4xl font-bold text-gray-400 px-6 py-4 rounded-lg">
                  VS
                </div>
                <div className="px-5 py-1.5 rounded-full bg-gray-100 text-gray-800 text-xs font-semibold border border-gray-200 mt-3">
                  {match.status}
                </div>
              </>
            )}
          </div>

          {/* Đội khách */}
          <div className="flex flex-col items-center text-center">
            {renderLogo(match.away_team?.logo_url, match.away_team?.name)}
            <div className="mt-4">
              <h4 className="font-bold text-gray-900 text-base md:text-lg leading-tight line-clamp-2">
                {match.away_team?.name || `Đội ${match.away_team_id}`}
              </h4>
            </div>
          </div>
        </div>
      </div>

      {/* Footer chỉ với nút xem chi tiết */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex justify-center">
          <span className="text-sm font-medium text-blue-600 group-hover:text-blue-800 transition-colors">
            Nhấn để xem chi tiết →
          </span>
        </div>
      </div>
    </div>
  );
};

export default MatchPost;
