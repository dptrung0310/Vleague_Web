import React, { useState, useEffect } from "react";
import matchService from "../services/matchService";
import {
  Loader,
  Target,
  Redo,
  UserCheck,
  AlertTriangle,
  Users,
  Calendar,
  MapPin,
  X,
  Award,
  User,
} from "lucide-react";

const MatchModal = ({ match, onClose }) => {
  const [activeTab, setActiveTab] = useState("stats");
  const [matchDetails, setMatchDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("🔍 MatchModal received match prop:", match);
  }, [match]);

  useEffect(() => {
    const fetchMatchDetails = async () => {
      if (!match) return;

      setLoading(true);
      setError(null);
      try {
        console.log(`📞 Fetching details for match ID: ${match.match_id}`);
        const response = await matchService.getMatchDetails(match.match_id);
        console.log("📦 API Response:", response);

        if (response && response.status === "success") {
          console.log("✅ API success, updating matchDetails");
          setMatchDetails(response.data);
        } else {
          console.warn("⚠️ API returned error:", response);
          setError(response?.message || "Không thể tải chi tiết trận đấu");
        }
      } catch (err) {
        console.error("❌ Error fetching match details:", err);
        setError("Không thể tải chi tiết trận đấu. Vui lòng thử lại sau.");
      } finally {
        setLoading(false);
      }
    };

    fetchMatchDetails();
  }, [match]);

  useEffect(() => {
    if (matchDetails) {
      console.log("✅ matchDetails state updated:", matchDetails);
      console.log("📊 Events:", matchDetails.events?.length || 0);
      console.log("👥 Lineups:", matchDetails.lineups?.length || 0);
      console.log("⚖️ Referees:", matchDetails.referees?.length || 0);

      if (matchDetails.events && matchDetails.events.length > 0) {
        console.log("📝 Event types found:", [
          ...new Set(matchDetails.events.map((e) => e.event_type)),
        ]);
      }
    }
  }, [matchDetails]);

  // Hàm lọc sự kiện theo loại - SỬA CHO ĐÚNG VỚI DATABASE
  const getEventsByType = (type) => {
    if (!matchDetails?.events) {
      console.log(`No events found for type: ${type}`);
      return [];
    }

    // Map tên sự kiện để hỗ trợ cả tiếng Việt và tiếng Anh
    const typeMapping = {
      "Bàn thắng": "goal",
      "Thẻ vàng": "yellow_card",
      "Thẻ đỏ": "red_card",
      goal: "goal",
      yellow_card: "yellow_card",
      red_card: "red_card",
    };

    const dbType = typeMapping[type] || type;
    const filtered = matchDetails.events.filter(
      (event) => event.event_type === dbType
    );

    console.log(
      `Looking for events of type: ${type} -> ${dbType}, found: ${filtered.length}`
    );
    return filtered;
  };

  // Hàm hiển thị tên sự kiện bằng tiếng Việt
  const getEventDisplayName = (eventType) => {
    const displayNames = {
      goal: "Bàn thắng",
      yellow_card: "Thẻ vàng",
      red_card: "Thẻ đỏ",
    };
    return displayNames[eventType] || eventType;
  };

  const getLineupsByTeam = (teamId) => {
    if (!matchDetails?.lineups) {
      console.log("No lineups data available");
      return { starters: [], substitutes: [] };
    }

    const targetTeamId = Number(teamId);
    const teamLineups = matchDetails.lineups.filter(
      (l) => Number(l.team_id) === targetTeamId
    );

    return {
      starters: teamLineups
        .filter((l) => l.is_starter)
        .sort((a, b) => a.shirt_number - b.shirt_number),
      substitutes: teamLineups
        .filter((l) => !l.is_starter)
        .sort((a, b) => a.shirt_number - b.shirt_number),
    };
  };

  if (!match) return null;

  const homeTeamId = match.home_team?.id || match.home_team_id;
  const awayTeamId = match.away_team?.id || match.away_team_id;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black bg-opacity-60 backdrop-blur-sm"
        onClick={onClose}
      ></div>

      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl h-[90vh] flex flex-col relative z-10 overflow-hidden animate-fade-in-up">
        {/* Header - Giữ nguyên màu trắng trên nền xanh */}
        <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white p-6 flex flex-col items-center relative shrink-0">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white hover:bg-white/20 p-2 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2 mb-2">
            <Calendar className="w-4 h-4" />
            <div className="text-sm opacity-90">
              {match.season_name} - Vòng {match.round}
            </div>
          </div>

          <div className="flex items-center gap-6 md:gap-8 w-full justify-center mb-2">
            <div className="text-center w-1/3">
              <div className="font-bold text-xl md:text-2xl truncate text-white">
                {match.home_team?.name || "Home Team"}
              </div>
              <div className="text-sm opacity-80 mt-1 text-white">
                {match.home_team?.short_name || ""}
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-3xl md:text-4xl font-black bg-white/20 px-4 py-3 rounded-xl backdrop-blur-md min-w-[100px] text-center text-white">
                {match.home_score || 0} - {match.away_score || 0}
              </div>
            </div>

            <div className="text-center w-1/3">
              <div className="font-bold text-xl md:text-2xl truncate text-white">
                {match.away_team?.name || "Away Team"}
              </div>
              <div className="text-sm opacity-80 mt-1 text-white">
                {match.away_team?.short_name || ""}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 text-sm opacity-80 text-white">
            <MapPin className="w-4 h-4" />
            <span>{match.stadium_name || "Unknown Stadium"}</span>
            <span className="mx-2">•</span>
            <span>
              {match.match_datetime
                ? new Date(match.match_datetime).toLocaleDateString("vi-VN")
                : "Unknown date"}
            </span>
          </div>
        </div>

        {/* Tab Navigation - Chỉnh màu chữ đen */}
        {/* Tab Navigation */}
        <div className="flex shrink-0 bg-blue-900 p-2 gap-2">
          {" "}
          {/* Nền xanh đậm, có khoảng cách */}
          <button
            onClick={() => setActiveTab("stats")}
            className={`flex-1 py-2 rounded-lg font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
              activeTab === "stats"
                ? "bg-blue-600 text-white shadow-md" // Active: Nền xanh sáng, chữ trắng
                : "text-blue-200 hover:bg-blue-800 hover:text-white" // Inactive: Chữ mờ, hover hiện nền
            }`}
          >
            <Target className="w-4 h-4" />
            Sự kiện
          </button>
          <button
            onClick={() => setActiveTab("lineups")}
            className={`flex-1 py-2 rounded-lg font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
              activeTab === "lineups"
                ? "bg-blue-600 text-white shadow-md"
                : "text-blue-200 hover:bg-blue-800 hover:text-white"
            }`}
          >
            <Users className="w-4 h-4" />
            Đội hình
          </button>
          <button
            onClick={() => setActiveTab("report")}
            className={`flex-1 py-2 rounded-lg font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
              activeTab === "report"
                ? "bg-blue-600 text-white shadow-md"
                : "text-blue-200 hover:bg-blue-800 hover:text-white"
            }`}
          >
            <Award className="w-4 h-4" />
            Trọng tài
          </button>
        </div>

        {/* Content Area - Chỉnh tất cả text thành màu đen/gray-900 */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-gray-50">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-gray-900">Đang tải chi tiết trận đấu...</p>
            </div>
          ) : error ? (
            <div className="text-center py-10">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-gray-900">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Thử lại
              </button>
            </div>
          ) : !matchDetails ? (
            <div className="text-center py-10">
              <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
              <p className="text-gray-900">Không có dữ liệu chi tiết</p>
              <button
                onClick={onClose}
                className="mt-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
              >
                Đóng
              </button>
            </div>
          ) : (
            <>
              {activeTab === "stats" && (
                <div className="space-y-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">
                    Diễn biến trận đấu
                  </h3>

                  {/* Bàn thắng */}
                  {getEventsByType("goal").length > 0 && (
                    <div className="bg-white rounded-lg shadow p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        <h4 className="font-semibold text-gray-900">
                          Bàn thắng
                        </h4>
                        <span className="text-sm text-gray-700 ml-2">
                          ({getEventsByType("goal").length})
                        </span>
                      </div>
                      <div className="space-y-2">
                        {getEventsByType("goal").map((event, index) => (
                          <div
                            key={event.event_id || index}
                            className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                          >
                            <div className="flex items-center gap-3">
                              <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded">
                                {event.minute}'
                              </span>
                              <span className="font-medium text-gray-900">
                                {event.player_name || "Không rõ"}
                              </span>
                              <span className="text-sm text-gray-700">
                                ({event.team_name || "Không rõ đội"})
                              </span>
                            </div>
                            <span className="text-sm text-gray-900">⚽</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Thẻ vàng */}
                  {getEventsByType("yellow_card").length > 0 && (
                    <div className="bg-white rounded-lg shadow p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                        <h4 className="font-semibold text-gray-900">
                          Thẻ vàng
                        </h4>
                        <span className="text-sm text-gray-700 ml-2">
                          ({getEventsByType("yellow_card").length})
                        </span>
                      </div>
                      <div className="space-y-2">
                        {getEventsByType("yellow_card").map((event, index) => (
                          <div
                            key={event.event_id || index}
                            className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                          >
                            <div className="flex items-center gap-3">
                              <span className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2 py-1 rounded">
                                {event.minute}'
                              </span>
                              <span className="text-gray-900">
                                {event.player_name || "Không rõ"}
                              </span>
                              <span className="text-sm text-gray-700">
                                ({event.team_name || "Không rõ đội"})
                              </span>
                            </div>
                            <span className="text-sm text-gray-900">🟨</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Thẻ đỏ */}
                  {getEventsByType("red_card").length > 0 && (
                    <div className="bg-white rounded-lg shadow p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <h4 className="font-semibold text-gray-900">Thẻ đỏ</h4>
                        <span className="text-sm text-gray-700 ml-2">
                          ({getEventsByType("red_card").length})
                        </span>
                      </div>
                      <div className="space-y-2">
                        {getEventsByType("red_card").map((event, index) => (
                          <div
                            key={event.event_id || index}
                            className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                          >
                            <div className="flex items-center gap-3">
                              <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded">
                                {event.minute}'
                              </span>
                              <span className="text-gray-900">
                                {event.player_name || "Không rõ"}
                              </span>
                              <span className="text-sm text-gray-700">
                                ({event.team_name || "Không rõ đội"})
                              </span>
                            </div>
                            <span className="text-sm text-gray-900">🟥</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {(!matchDetails?.events ||
                    matchDetails.events.length === 0) && (
                    <div className="text-center py-10">
                      <p className="text-gray-700">
                        Không có sự kiện nào được ghi nhận trong trận đấu này
                      </p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === "lineups" && (
                <div className="space-y-8">
                  <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="bg-blue-50 px-4 py-3 border-b">
                      <h4 className="font-bold text-gray-900">
                        {match.home_team?.name || "Đội nhà"} - Đội hình xuất
                        phát
                      </h4>
                    </div>
                    <div className="p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {getLineupsByTeam(homeTeamId).starters.map(
                          (player, index) => (
                            <div
                              key={player.lineup_id || index}
                              className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg"
                            >
                              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center font-bold text-blue-700">
                                {player.shirt_number || index + 1}
                              </div>
                              <div className="flex-1">
                                <div className="font-medium text-gray-900">
                                  {player.player_name || `Cầu thủ ${index + 1}`}
                                </div>
                                <div className="text-sm text-gray-700">
                                  {player.position || "Chưa rõ vị trí"}
                                </div>
                              </div>
                              <UserCheck className="w-5 h-5 text-green-500" />
                            </div>
                          )
                        )}
                      </div>

                      {getLineupsByTeam(homeTeamId).substitutes.length > 0 && (
                        <>
                          <div className="mt-6 mb-3 text-sm font-semibold text-gray-900">
                            Cầu thủ dự bị (
                            {getLineupsByTeam(homeTeamId).substitutes.length})
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {getLineupsByTeam(homeTeamId).substitutes.map(
                              (player, index) => (
                                <div
                                  key={player.lineup_id || `sub-${index}`}
                                  className="flex items-center gap-3 p-2"
                                >
                                  <div className="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center font-medium text-gray-700">
                                    {player.shirt_number || index + 12}
                                  </div>
                                  <div className="flex-1">
                                    <div className="font-medium text-sm text-gray-900">
                                      {player.player_name ||
                                        `Dự bị ${index + 1}`}
                                    </div>
                                  </div>
                                  <Redo className="w-4 h-4 text-gray-400" />
                                </div>
                              )
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="bg-red-50 px-4 py-3 border-b">
                      <h4 className="font-bold text-gray-900">
                        {match.away_team?.name || "Đội khách"} - Đội hình xuất
                        phát
                      </h4>
                    </div>
                    <div className="p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {getLineupsByTeam(awayTeamId).starters.map(
                          (player, index) => (
                            <div
                              key={player.lineup_id || `away-${index}`}
                              className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg"
                            >
                              <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center font-bold text-red-700">
                                {player.shirt_number || index + 1}
                              </div>
                              <div className="flex-1">
                                <div className="font-medium text-gray-900">
                                  {player.player_name || `Cầu thủ ${index + 1}`}
                                </div>
                                <div className="text-sm text-gray-700">
                                  {player.position || "Chưa rõ vị trí"}
                                </div>
                              </div>
                              <UserCheck className="w-5 h-5 text-green-500" />
                            </div>
                          )
                        )}
                      </div>

                      {getLineupsByTeam(awayTeamId).substitutes.length > 0 && (
                        <>
                          <div className="mt-6 mb-3 text-sm font-semibold text-gray-900">
                            Cầu thủ dự bị (
                            {getLineupsByTeam(awayTeamId).substitutes.length})
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {getLineupsByTeam(awayTeamId).substitutes.map(
                              (player, index) => (
                                <div
                                  key={player.lineup_id || `away-sub-${index}`}
                                  className="flex items-center gap-3 p-2"
                                >
                                  <div className="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center font-medium text-gray-700">
                                    {player.shirt_number || index + 12}
                                  </div>
                                  <div className="flex-1">
                                    <div className="font-medium text-sm text-gray-900">
                                      {player.player_name ||
                                        `Dự bị ${index + 1}`}
                                    </div>
                                  </div>
                                  <Redo className="w-4 h-4 text-gray-400" />
                                </div>
                              )
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "report" && (
                <div className="space-y-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">
                    Ban tổ chức trận đấu
                  </h3>

                  {matchDetails?.referees &&
                  matchDetails.referees.length > 0 ? (
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {matchDetails.referees.map((referee, index) => (
                          <div
                            key={referee.referee_id || index}
                            className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg"
                          >
                            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                              <User className="w-6 h-6 text-blue-600" />
                            </div>
                            <div>
                              <div className="font-bold text-gray-900">
                                {referee.full_name ||
                                  referee.referee_name ||
                                  "Không rõ tên"}
                              </div>
                              <div className="text-sm text-gray-700 capitalize">
                                {referee.role || "Trọng tài"}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-10">
                      <p className="text-gray-700">
                        Không có thông tin về ban tổ chức trận đấu
                      </p>
                    </div>
                  )}

                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-6">
                    <h4 className="font-bold text-gray-900 mb-3">
                      Thông tin trận đấu
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-700">
                          Sân vận động
                        </div>
                        <div className="font-medium text-gray-900">
                          {match.stadium_name || "Không rõ"}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-700">Thời gian</div>
                        <div className="font-medium text-gray-900">
                          {match.match_datetime
                            ? new Date(match.match_datetime).toLocaleString(
                                "vi-VN"
                              )
                            : "Không rõ"}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-700">Mùa giải</div>
                        <div className="font-medium text-gray-900">
                          {match.season_name || "Không rõ"}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-700">Vòng đấu</div>
                        <div className="font-medium text-gray-900">
                          Vòng {match.round || "?"}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default MatchModal;
