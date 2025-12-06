// src/pages/Players/Players.jsx
import React, { useState, useEffect } from "react";
import {
  Search,
  X,
  Target,
  Flag,
  Shirt,
  ChevronDown,
  Users,
  Trophy,
} from "lucide-react";
import seasonService from "../../services/seasonService";
import teamService from "../../services/teamService";

const Players = () => {
  const [seasons, setSeasons] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState(null);
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [players, setPlayers] = useState([]);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState("goals");
  const [visiblePlayers, setVisiblePlayers] = useState(12);

  // Fetch danh sách mùa giải
  useEffect(() => {
    const fetchSeasons = async () => {
      try {
        const response = await seasonService.getAllSeasons();
        if (response.status === "success") {
          setSeasons(response.data);
          if (response.data.length > 0) {
            setSelectedSeason(response.data[0].season_id);
          }
        }
      } catch (error) {
        console.error("Error fetching seasons:", error);
      }
    };

    fetchSeasons();
  }, []);

  // Fetch danh sách đội theo mùa
  useEffect(() => {
    const fetchTeamsBySeason = async () => {
      if (!selectedSeason) return;

      try {
        const response = await teamService.getTeamsBySeason(selectedSeason);
        if (response.status === "success") {
          setTeams(response.data);
          setSelectedTeam(null);
        }
      } catch (error) {
        console.error("Error fetching teams:", error);
      }
    };

    fetchTeamsBySeason();
  }, [selectedSeason]);

  // Fetch danh sách cầu thủ
  useEffect(() => {
    const fetchPlayers = async () => {
      if (!selectedSeason) return;

      setLoading(true);
      try {
        let url = `/api/players/season/${selectedSeason}`;
        if (selectedTeam) {
          url += `?team_id=${selectedTeam}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.status === "success") {
          const sortedPlayers = sortPlayers(data.data, sortBy);
          setPlayers(sortedPlayers);
          setFilteredPlayers(sortedPlayers);
          setVisiblePlayers(12); // Reset về 12 mỗi khi filter thay đổi
        }
      } catch (error) {
        console.error("Error fetching players:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayers();
  }, [selectedSeason, selectedTeam, sortBy]);

  // Tìm kiếm cầu thủ
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredPlayers(players);
    } else {
      const filtered = players.filter((player) =>
        player.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredPlayers(filtered);
    }
    setVisiblePlayers(12); // Reset về 12 khi tìm kiếm
  }, [searchTerm, players]);

  // Sắp xếp cầu thủ
  const sortPlayers = (playersList, criteria) => {
    return [...playersList].sort((a, b) => {
      switch (criteria) {
        case "goals":
          return (b.statistics?.goals || 0) - (a.statistics?.goals || 0);
        case "yellow_cards":
          return (
            (b.statistics?.yellow_cards || 0) -
            (a.statistics?.yellow_cards || 0)
          );
        case "red_cards":
          return (
            (b.statistics?.red_cards || 0) - (a.statistics?.red_cards || 0)
          );
        default:
          return 0;
      }
    });
  };

  const handleSortChange = (criteria) => {
    setSortBy(criteria);
    const sorted = sortPlayers(players, criteria);
    setPlayers(sorted);
    setFilteredPlayers(sorted);
    setVisiblePlayers(12);
  };

  const clearSearch = () => {
    setSearchTerm("");
  };

  const loadMorePlayers = () => {
    setVisiblePlayers((prev) => prev + 12);
  };

  const getPositionBadge = (position) => {
    if (!position) return null;

    const lowerPosition = position.toLowerCase();
    if (
      lowerPosition.includes("thủ môn") ||
      lowerPosition.includes("goalkeeper")
    )
      return { color: "bg-blue-100 text-blue-800", label: "TM" };
    if (lowerPosition.includes("hậu vệ") || lowerPosition.includes("defender"))
      return { color: "bg-green-100 text-green-800", label: "HV" };
    if (
      lowerPosition.includes("tiền vệ") ||
      lowerPosition.includes("midfielder")
    )
      return { color: "bg-yellow-100 text-yellow-800", label: "TV" };
    if (lowerPosition.includes("tiền đạo") || lowerPosition.includes("forward"))
      return { color: "bg-red-100 text-red-800", label: "TĐ" };
    return {
      color: "bg-gray-100 text-gray-800",
      label: position.substring(0, 2).toUpperCase(),
    };
  };

  const getStatEmoji = (type, value) => {
    if (type === "goals") {
      if (value >= 10) return "🔥";
      if (value >= 5) return "⚽";
      if (value >= 1) return "🎯";
      return "";
    }
    if (type === "yellow_cards") {
      if (value >= 5) return "🟨🟨🟨";
      if (value >= 3) return "🟨🟨";
      if (value >= 1) return "🟨";
      return "";
    }
    if (type === "red_cards") {
      if (value >= 2) return "🟥🟥";
      if (value >= 1) return "🟥";
      return "";
    }
    return "";
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Danh Sách Cầu Thủ
          </h1>
          <p className="text-gray-600">
            Thống kê theo số bàn thắng, thẻ vàng và thẻ đỏ
          </p>
        </div>
        {/* Filter Section - ĐƠN GIẢN */}
        <div className="bg-gradient-to-r from-blue-50 to-white rounded-xl shadow p-6 mb-6 border border-blue-100">
          {/* Season & Team Selector */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* Season - MÀU SÁNG */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mùa giải
              </label>
              <div className="relative">
                <select
                  value={selectedSeason || ""}
                  onChange={(e) => setSelectedSeason(Number(e.target.value))}
                  className="w-full px-4 py-3 bg-white border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400 appearance-none transition-all hover:border-blue-300"
                >
                  {seasons.map((season) => (
                    <option key={season.season_id} value={season.season_id}>
                      {season.name}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-3.5 w-5 h-5 text-blue-400 pointer-events-none" />
              </div>
            </div>

            {/* Team - MÀU SÁNG */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Đội bóng
              </label>
              <div className="relative">
                <select
                  value={selectedTeam || ""}
                  onChange={(e) =>
                    setSelectedTeam(
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                  className="w-full px-4 py-3 bg-white border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400 appearance-none transition-all hover:border-blue-300"
                >
                  <option value="">Tất cả đội</option>
                  {teams.map((team) => (
                    <option key={team.team_id} value={team.team_id}>
                      {team.name}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-3.5 w-5 h-5 text-blue-400 pointer-events-none" />
              </div>
            </div>
          </div>

          {/* Search - MÀU SÁNG */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tìm cầu thủ
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="Nhập tên cầu thủ..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-3 pl-12 bg-white border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all hover:border-blue-300"
              />
              <Search className="absolute left-4 top-3.5 w-5 h-5 text-blue-400" />
              {searchTerm && (
                <button
                  onClick={clearSearch}
                  className="absolute right-3 top-3.5 text-blue-400 hover:text-blue-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>

          {/* Sort Buttons - CHỈ 3 LỰA CHỌN (ĐỔI MÀU SÁNG HƠN) */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => handleSortChange("goals")}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all flex-1 min-w-[200px] ${
                sortBy === "goals"
                  ? "bg-gradient-to-r from-blue-100 to-blue-50 border-2 border-blue-300 text-blue-700 shadow-md"
                  : "bg-white border border-blue-200 text-gray-700 hover:bg-blue-50 hover:border-blue-300"
              }`}
            >
              <Target className="w-5 h-5" />
              <span className="font-medium">Số bàn thắng</span>
              <span className="ml-auto font-bold">
                {sortBy === "goals" && "↓"}
              </span>
            </button>

            <button
              onClick={() => handleSortChange("yellow_cards")}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all flex-1 min-w-[200px] ${
                sortBy === "yellow_cards"
                  ? "bg-gradient-to-r from-yellow-100 to-yellow-50 border-2 border-yellow-300 text-yellow-700 shadow-md"
                  : "bg-white border border-blue-200 text-gray-700 hover:bg-yellow-50 hover:border-yellow-300"
              }`}
            >
              <Flag className="w-5 h-5" />
              <span className="font-medium">Thẻ vàng</span>
              <span className="ml-auto font-bold">
                {sortBy === "yellow_cards" && "↓"}
              </span>
            </button>

            <button
              onClick={() => handleSortChange("red_cards")}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all flex-1 min-w-[200px] ${
                sortBy === "red_cards"
                  ? "bg-gradient-to-r from-red-100 to-red-50 border-2 border-red-300 text-red-700 shadow-md"
                  : "bg-white border border-blue-200 text-gray-700 hover:bg-red-50 hover:border-red-300"
              }`}
            >
              <Flag className="w-5 h-5" />
              <span className="font-medium">Thẻ đỏ</span>
              <span className="ml-auto font-bold">
                {sortBy === "red_cards" && "↓"}
              </span>
            </button>
          </div>
        </div>
        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-500"></div>
            <p className="mt-4 text-gray-600">Đang tải dữ liệu cầu thủ...</p>
          </div>
        )}
        {/* Players Grid */}
        {!loading && filteredPlayers.length > 0 && (
          <>
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-800">
                    {sortBy === "goals" && "Vua phá lưới"}
                    {sortBy === "yellow_cards" && "Nhiều thẻ vàng nhất"}
                    {sortBy === "red_cards" && "Nhiều thẻ đỏ nhất"}
                  </h2>
                  <p className="text-gray-600">
                    Hiển thị {Math.min(visiblePlayers, filteredPlayers.length)}{" "}
                    trong tổng số {filteredPlayers.length} cầu thủ
                  </p>
                </div>
                {selectedTeam &&
                  teams.find((t) => t.team_id === selectedTeam) && (
                    <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
                      <img
                        src={
                          teams.find((t) => t.team_id === selectedTeam).logo_url
                        }
                        alt="Team"
                        className="w-6 h-6 object-contain"
                        onError={(e) => (e.target.style.display = "none")}
                      />
                      <span className="font-medium">
                        {teams.find((t) => t.team_id === selectedTeam).name}
                      </span>
                    </div>
                  )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredPlayers.slice(0, visiblePlayers).map((player, index) => {
                const positionBadge = getPositionBadge(player.position);

                return (
                  <div
                    key={player.player_id}
                    className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 hover:shadow-xl transition-all"
                  >
                    {/* Top Rank Badge for Top 3 */}
                    {index < 3 && sortBy === "goals" && (
                      <div
                        className={`absolute top-2 left-2 w-8 h-8 rounded-full flex items-center justify-center text-white font-bold z-10 ${
                          index === 0
                            ? "bg-yellow-500"
                            : index === 1
                            ? "bg-gray-400"
                            : "bg-amber-700"
                        }`}
                      >
                        {index === 0 ? "🏆" : index + 1}
                      </div>
                    )}

                    {/* Player Card */}
                    <div className="p-4">
                      {/* Player Info Row */}
                      <div className="flex items-center gap-3 mb-3">
                        {/* Player Image */}
                        <div className="w-16 h-16 rounded-full overflow-hidden bg-gradient-to-br from-blue-100 to-gray-100 border-2 border-gray-300">
                          {player.image_url ? (
                            <img
                              src={player.image_url}
                              alt={player.full_name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <Users className="w-8 h-8 text-gray-400" />
                            </div>
                          )}
                        </div>

                        {/* Player Details */}
                        <div className="flex-1">
                          <h3 className="font-bold text-lg text-gray-800 truncate">
                            {player.full_name}
                          </h3>
                          <div className="flex items-center gap-2 mt-1">
                            <Shirt className="w-4 h-4 text-gray-500" />
                            <span className="text-sm text-gray-600 truncate">
                              {player.team_name}
                            </span>
                            {player.shirt_number && (
                              <span className="text-xs bg-gray-200 px-2 py-0.5 rounded">
                                #{player.shirt_number}
                              </span>
                            )}
                          </div>
                          {positionBadge && (
                            <div className="mt-1">
                              <span
                                className={`text-xs px-2 py-1 rounded ${positionBadge.color}`}
                              >
                                {positionBadge.label}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Statistics */}
                      <div className="bg-gray-50 rounded-lg p-3 mt-3">
                        <div className="grid grid-cols-3 gap-3">
                          {/* Goals */}
                          <div className="text-center">
                            <div className="text-2xl font-bold text-red-600">
                              {player.statistics?.goals || 0}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              Bàn thắng
                            </div>
                            <div className="text-xs text-gray-400 mt-1">
                              {getStatEmoji(
                                "goals",
                                player.statistics?.goals || 0
                              )}
                            </div>
                          </div>

                          {/* Yellow Cards */}
                          <div className="text-center">
                            <div className="text-2xl font-bold text-yellow-600">
                              {player.statistics?.yellow_cards || 0}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              Thẻ vàng
                            </div>
                            <div className="text-xs text-gray-400 mt-1">
                              {getStatEmoji(
                                "yellow_cards",
                                player.statistics?.yellow_cards || 0
                              )}
                            </div>
                          </div>

                          {/* Red Cards */}
                          <div className="text-center">
                            <div className="text-2xl font-bold text-red-700">
                              {player.statistics?.red_cards || 0}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              Thẻ đỏ
                            </div>
                            <div className="text-xs text-gray-400 mt-1">
                              {getStatEmoji(
                                "red_cards",
                                player.statistics?.red_cards || 0
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Load More Button */}
            {visiblePlayers < filteredPlayers.length && (
              <div className="mt-8 text-center">
                <button
                  onClick={loadMorePlayers}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-medium rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md hover:shadow-lg"
                >
                  Xem thêm cầu thủ ({filteredPlayers.length - visiblePlayers}{" "}
                  cầu thủ còn lại)
                </button>
                <p className="text-sm text-gray-500 mt-2">
                  Đang hiển thị{" "}
                  {Math.min(visiblePlayers, filteredPlayers.length)} /{" "}
                  {filteredPlayers.length} cầu thủ
                </p>
              </div>
            )}
          </>
        )}
        {/* No Results */}
        {!loading && filteredPlayers.length === 0 && (
          <div className="text-center py-16 bg-white rounded-xl shadow border border-gray-200">
            <Users className="w-16 h-16 mx-auto text-gray-300 mb-6" />
            <h3 className="text-2xl font-bold text-gray-700 mb-3">
              Không tìm thấy cầu thủ
            </h3>
            <p className="text-gray-500 mb-8 max-w-md mx-auto">
              {searchTerm
                ? `Không có cầu thủ nào phù hợp với "${searchTerm}"`
                : "Không có cầu thủ nào trong mùa giải này"}
            </p>
            {searchTerm && (
              <button
                onClick={clearSearch}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Xóa tìm kiếm
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Players;
