import React, { useState, useEffect } from "react";
import {
  Calendar,
  Search,
  Trophy,
  Users,
  ChevronDown,
  ChevronRight,
  BarChart3,
  Shirt,
  MapPin,
  Target,
  X,
  Filter,
  Award,
  TrendingUp,
  TrendingDown,
  Hash,
  ArrowUpDown,
} from "lucide-react";
import seasonService from "../../services/seasonService";
import teamService from "../../services/teamService";

const Teams = () => {
  const [seasons, setSeasons] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState(null);
  const [teams, setTeams] = useState([]);
  const [filteredTeams, setFilteredTeams] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [expandedTeam, setExpandedTeam] = useState(null);
  const [teamDetails, setTeamDetails] = useState({});
  const [sortBy, setSortBy] = useState("position"); // position, goal_difference, losses, wins

  // Fetch danh sách mùa giải
  useEffect(() => {
    const loadSeasons = async () => {
      try {
        setLoading(true);
        const response = await seasonService.getAllSeasons();
        if (response && response.status === "success") {
          setSeasons(response.data);
          if (response.data.length > 0) {
            setSelectedSeason(response.data[0].season_id);
          }
        }
      } catch (error) {
        console.error("Error loading seasons:", error);
      } finally {
        setLoading(false);
      }
    };

    loadSeasons();
  }, []);

  // Fetch danh sách đội theo mùa
  useEffect(() => {
    const loadTeamsBySeason = async () => {
      if (!selectedSeason) return;

      setLoading(true);
      try {
        const response = await teamService.getTeamsBySeason(selectedSeason);

        let teamsData = [];
        if (response && response.status === "success" && response.data) {
          teamsData = response.data;
        } else if (Array.isArray(response)) {
          teamsData = response;
        }

        const sortedTeams = sortTeams(teamsData, sortBy);
        setTeams(sortedTeams);
        setFilteredTeams(sortedTeams);
      } catch (error) {
        console.error("Error loading teams:", error);
      } finally {
        setLoading(false);
      }
    };

    loadTeamsBySeason();
  }, [selectedSeason, sortBy]);

  // Filter teams based on search
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredTeams(teams);
    } else {
      const filtered = teams.filter((team) =>
        team.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredTeams(filtered);
    }
  }, [searchTerm, teams]);

  // Sort teams function
  const sortTeams = (teamsList, sortCriteria) => {
    return [...teamsList].sort((a, b) => {
      switch (sortCriteria) {
        case "position":
          const posA = a.standing?.position || 999;
          const posB = b.standing?.position || 999;
          return posA - posB;

        case "goal_difference":
          const gdA = a.standing?.goal_difference || 0;
          const gdB = b.standing?.goal_difference || 0;
          return gdB - gdA; // Hiệu số cao nhất lên đầu

        case "losses":
          const lossesA = a.standing?.losses || 0;
          const lossesB = b.standing?.losses || 0;
          return lossesB - lossesA; // Nhiều trận thua nhất lên đầu

        case "wins":
          const winsA = a.standing?.wins || 0;
          const winsB = b.standing?.wins || 0;
          return winsB - winsA; // Nhiều trận thắng nhất lên đầu

        default:
          return 0;
      }
    });
  };

  // Handle sort change
  const handleSortChange = (criteria) => {
    setSortBy(criteria);
    const sorted = sortTeams(teams, criteria);
    setTeams(sorted);
    setFilteredTeams(sorted);
  };

  // Fetch team details when expanded
  const fetchTeamDetails = async (teamId) => {
    if (teamDetails[teamId]) return;

    try {
      const response = await teamService.getTeamSeasonDetails(
        teamId,
        selectedSeason
      );
      if (response && response.status === "success") {
        setTeamDetails((prev) => ({
          ...prev,
          [teamId]: response.data,
        }));
      }
    } catch (error) {
      console.error("Error fetching team details:", error);
    }
  };

  const handleTeamExpand = (teamId) => {
    if (expandedTeam === teamId) {
      setExpandedTeam(null);
    } else {
      setExpandedTeam(teamId);
      fetchTeamDetails(teamId);
    }
  };

  const getPositionColor = (position) => {
    if (position === 1)
      return "bg-gradient-to-r from-yellow-500 to-yellow-600 text-white";
    if (position === 2)
      return "bg-gradient-to-r from-gray-400 to-gray-500 text-white";
    if (position === 3)
      return "bg-gradient-to-r from-amber-700 to-amber-800 text-white";
    if (position <= 6)
      return "bg-gradient-to-r from-blue-500 to-blue-600 text-white";
    return "bg-gradient-to-r from-gray-200 to-gray-300 text-gray-800";
  };

  const getPositionIcon = (position) => {
    if (position === 1) return <Trophy className="w-4 h-4 mr-1" />;
    if (position === 2) return <Award className="w-4 h-4 mr-1" />;
    if (position === 3) return <Award className="w-4 h-4 mr-1" />;
    return <Hash className="w-4 h-4 mr-1" />;
  };

  // Clear search
  const clearSearch = () => {
    setSearchTerm("");
  };

  // Reset expanded team when season changes
  useEffect(() => {
    setExpandedTeam(null);
    setTeamDetails({});
  }, [selectedSeason]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-4xl font-bold text-gray-800 mb-3">
            Đội Bóng V-League
          </h1>
          <p className="text-gray-600 max-w-3xl">
            Khám phá thông tin chi tiết về các đội bóng, cầu thủ và thành tích
            thi đấu qua từng mùa giải. Xem bảng xếp hạng, thống kê và đội hình
            của từng đội.
          </p>
        </div>

        {/* Filter & Search Section */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-8 border border-gray-200">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Season Selector */}
            <div>
              <label className="flex items-center text-sm font-semibold text-gray-700 mb-3">
                <Calendar className="w-5 h-5 mr-2 text-blue-600" />
                Mùa Giải
              </label>
              <div className="relative">
                <select
                  value={selectedSeason || ""}
                  onChange={(e) => setSelectedSeason(Number(e.target.value))}
                  className="w-full px-4 py-3 pl-12 bg-gray-50 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all appearance-none"
                  disabled={loading}
                >
                  {seasons.map((season) => (
                    <option key={season.season_id} value={season.season_id}>
                      {season.name}{" "}
                      {season.start_date
                        ? `(${new Date(season.start_date).getFullYear()})`
                        : ""}
                    </option>
                  ))}
                </select>
                <Calendar className="absolute left-4 top-3.5 w-5 h-5 text-gray-500 pointer-events-none" />
              </div>
            </div>

            {/* Search */}
            <div>
              <label className="flex items-center text-sm font-semibold text-gray-700 mb-3">
                <Search className="w-5 h-5 mr-2 text-blue-600" />
                Tìm Đội Bóng
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Nhập tên đội bóng..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-3 pl-12 pr-10 bg-gray-50 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                />
                <Search className="absolute left-4 top-3.5 w-5 h-5 text-gray-500" />
                {searchTerm && (
                  <button
                    onClick={clearSearch}
                    className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Sort Options - ĐƠN GIẢN HÓA */}
          <div className="mt-6">
            <label className="flex items-center text-sm font-semibold text-gray-700 mb-3">
              <ArrowUpDown className="w-5 h-5 mr-2 text-blue-600" />
              Sắp xếp theo
            </label>
            <div className="flex flex-wrap gap-2">
              {[
                {
                  key: "position",
                  label: "Thứ hạng",
                  icon: <Trophy className="w-4 h-4" />,
                  description: "Vị trí trên BXH",
                },
                {
                  key: "goal_difference",
                  label: "Hiệu số",
                  icon: <TrendingUp className="w-4 h-4" />,
                  description: "Hiệu số bàn thắng - thua",
                },
                {
                  key: "losses",
                  label: "Trận thua",
                  icon: <TrendingDown className="w-4 h-4" />,
                  description: "Số trận thua",
                },
                {
                  key: "wins",
                  label: "Trận thắng",
                  icon: <TrendingUp className="w-4 h-4" />,
                  description: "Số trận thắng",
                },
              ].map((sortOption) => (
                <button
                  key={sortOption.key}
                  onClick={() => handleSortChange(sortOption.key)}
                  className={`flex flex-col items-start p-3 rounded-xl border transition-all min-w-[120px] ${
                    sortBy === sortOption.key
                      ? "bg-blue-50 text-blue-700 border-blue-300 shadow-md"
                      : "bg-gray-50 text-gray-700 border-gray-300 hover:bg-gray-100"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {sortOption.icon}
                    <span className="font-semibold">{sortOption.label}</span>
                  </div>
                  <div className="text-xs text-gray-500 text-left">
                    {sortOption.description}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Stats Summary - ĐƠN GIẢN HÓA */}
        {!loading && teams.length > 0 && (
          <div className="mb-8 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl shadow border-l-4 border-blue-500">
              <div className="text-2xl font-bold text-gray-800">
                {teams.length}
              </div>
              <div className="text-sm text-gray-600">Tổng số đội</div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
            <p className="mt-6 text-lg text-gray-600">
              Đang tải dữ liệu đội bóng...
            </p>
          </div>
        )}

        {/* Teams Grid */}
        {!loading && (
          <div className="space-y-6">
            {filteredTeams.map((team) => (
              <div
                key={team.team_id}
                className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-200 hover:shadow-xl transition-shadow duration-300"
              >
                {/* Team Header */}
                <div
                  className="p-6 cursor-pointer hover:bg-gray-50 transition-colors duration-200"
                  onClick={() => handleTeamExpand(team.team_id)}
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between">
                    <div className="flex items-center space-x-5 mb-4 md:mb-0">
                      {/* Team Logo */}
                      <div className="relative">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-gray-100 rounded-xl p-2 flex items-center justify-center border-2 border-gray-300 shadow-md">
                          {team.logo_url ? (
                            <img
                              src={team.logo_url}
                              alt={team.name}
                              className="w-full h-full object-contain"
                              onError={(e) => {
                                e.target.style.display = "none";
                                e.target.parentElement.innerHTML =
                                  '<Users className="w-8 h-8 text-gray-400" />';
                              }}
                            />
                          ) : (
                            <Users className="w-8 h-8 text-gray-400" />
                          )}
                        </div>
                        {team.standing?.position && (
                          <div
                            className={`absolute -top-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shadow-lg ${getPositionColor(
                              team.standing.position
                            )}`}
                          >
                            <div className="flex items-center">
                              {getPositionIcon(team.standing.position)}
                              <span className="text-xs">
                                {team.standing.position}
                              </span>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Team Info */}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-xl font-bold text-gray-800">
                            {team.name}
                          </h3>
                          {team.standing?.position === 1 && (
                            <span className="px-2 py-0.5 bg-gradient-to-r from-yellow-100 to-yellow-200 text-yellow-800 text-xs font-bold rounded-full">
                              VÔ ĐỊCH
                            </span>
                          )}
                        </div>

                        {team.home_stadium && (
                          <div className="flex items-center text-gray-600 text-sm">
                            <MapPin className="w-3.5 h-3.5 mr-1.5 flex-shrink-0" />
                            <span className="truncate">
                              {team.home_stadium.name}, {team.home_stadium.city}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Stats & Expand Button */}
                    <div className="flex items-center justify-between md:justify-end space-x-4">
                      {/* Quick Stats - HIỂN THỊ RÕ RÀNG HƠN */}
                      {team.standing && (
                        <div className="hidden md:flex items-center space-x-4">
                          <div className="text-center min-w-[60px]">
                            <div className="text-lg font-bold text-blue-600">
                              {team.standing.points}
                            </div>
                            <div className="text-xs text-gray-500">Điểm</div>
                          </div>
                          <div className="text-center min-w-[60px]">
                            <div
                              className={`text-lg font-bold ${
                                team.standing.goal_difference > 0
                                  ? "text-green-600"
                                  : team.standing.goal_difference < 0
                                  ? "text-red-600"
                                  : "text-gray-600"
                              }`}
                            >
                              {team.standing.goal_difference > 0 ? "+" : ""}
                              {team.standing.goal_difference}
                            </div>
                            <div className="text-xs text-gray-500">Hiệu số</div>
                          </div>
                          <div className="text-center min-w-[60px]">
                            <div className="text-lg font-bold text-green-600">
                              {team.standing.wins}
                            </div>
                            <div className="text-xs text-gray-500">Thắng</div>
                          </div>
                          <div className="text-center min-w-[60px]">
                            <div className="text-lg font-bold text-red-600">
                              {team.standing.losses}
                            </div>
                            <div className="text-xs text-gray-500">Thua</div>
                          </div>
                        </div>
                      )}

                      {/* Expand Button */}
                      <div className="flex items-center">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleTeamExpand(team.team_id);
                          }}
                          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
                            expandedTeam === team.team_id
                              ? "bg-blue-100 text-blue-700"
                              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                          }`}
                        >
                          <span className="text-sm">
                            {expandedTeam === team.team_id ? "Ẩn" : "Chi tiết"}
                          </span>
                          <ChevronRight
                            className={`w-4 h-4 transition-transform duration-300 ${
                              expandedTeam === team.team_id ? "rotate-90" : ""
                            }`}
                          />
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Mobile Quick Stats */}
                  {team.standing && (
                    <div className="mt-4 md:hidden grid grid-cols-4 gap-2">
                      <div className="text-center bg-gray-50 p-2 rounded-lg">
                        <div className="text-lg font-bold text-blue-600">
                          {team.standing.points}
                        </div>
                        <div className="text-xs text-gray-500">Điểm</div>
                      </div>
                      <div className="text-center bg-gray-50 p-2 rounded-lg">
                        <div
                          className={`text-lg font-bold ${
                            team.standing.goal_difference > 0
                              ? "text-green-600"
                              : team.standing.goal_difference < 0
                              ? "text-red-600"
                              : "text-gray-600"
                          }`}
                        >
                          {team.standing.goal_difference > 0 ? "+" : ""}
                          {team.standing.goal_difference}
                        </div>
                        <div className="text-xs text-gray-500">Hiệu số</div>
                      </div>
                      <div className="text-center bg-gray-50 p-2 rounded-lg">
                        <div className="text-lg font-bold text-green-600">
                          {team.standing.wins}
                        </div>
                        <div className="text-xs text-gray-500">Thắng</div>
                      </div>
                      <div className="text-center bg-gray-50 p-2 rounded-lg">
                        <div className="text-lg font-bold text-red-600">
                          {team.standing.losses}
                        </div>
                        <div className="text-xs text-gray-500">Thua</div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Expanded Details */}
                {expandedTeam === team.team_id && (
                  <div className="border-t border-gray-200 p-6 bg-gradient-to-br from-gray-50 to-blue-50">
                    {/* Detailed Stats */}
                    {teamDetails[team.team_id]?.standing && (
                      <div className="mb-8">
                        <div className="flex items-center mb-6">
                          <BarChart3 className="w-6 h-6 mr-3 text-blue-600" />
                          <h4 className="text-lg font-bold text-gray-800">
                            Thống Kê Chi Tiết
                          </h4>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          {[
                            {
                              label: "Số Trận",
                              value: teamDetails[team.team_id].standing.played,
                              color: "bg-blue-50 text-blue-700 border-blue-200",
                            },
                            {
                              label: "Thắng",
                              value: teamDetails[team.team_id].standing.wins,
                              color:
                                "bg-green-50 text-green-700 border-green-200",
                            },
                            {
                              label: "Hòa",
                              value: teamDetails[team.team_id].standing.draws,
                              color:
                                "bg-yellow-50 text-yellow-700 border-yellow-200",
                            },
                            {
                              label: "Thua",
                              value: teamDetails[team.team_id].standing.losses,
                              color: "bg-red-50 text-red-700 border-red-200",
                            },
                            {
                              label: "Bàn Thắng",
                              value:
                                teamDetails[team.team_id].standing.goals_for,
                              color:
                                "bg-purple-50 text-purple-700 border-purple-200",
                            },
                            {
                              label: "Bàn Thua",
                              value:
                                teamDetails[team.team_id].standing
                                  .goals_against,
                              color: "bg-pink-50 text-pink-700 border-pink-200",
                            },
                            {
                              label: "Hiệu Số",
                              value:
                                teamDetails[team.team_id].standing
                                  .goal_difference,
                              color:
                                teamDetails[team.team_id].standing
                                  .goal_difference > 0
                                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                                  : teamDetails[team.team_id].standing
                                      .goal_difference < 0
                                  ? "bg-rose-50 text-rose-700 border-rose-200"
                                  : "bg-gray-50 text-gray-700 border-gray-200",
                            },
                            {
                              label: "Điểm",
                              value: teamDetails[team.team_id].standing.points,
                              color:
                                "bg-indigo-50 text-indigo-700 border-indigo-200",
                            },
                          ].map((stat, idx) => (
                            <div
                              key={idx}
                              className={`${stat.color} p-3 rounded-xl border`}
                            >
                              <div className="text-xl font-bold mb-1">
                                {stat.value}
                              </div>
                              <div className="text-xs font-medium">
                                {stat.label}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Players Section */}
                    {teamDetails[team.team_id]?.players &&
                      teamDetails[team.team_id].players.length > 0 && (
                        <div>
                          <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center">
                              <Shirt className="w-5 h-5 mr-2 text-blue-600" />
                              <h4 className="text-lg font-bold text-gray-800">
                                Đội Hình Cầu Thủ
                              </h4>
                            </div>
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                              {teamDetails[team.team_id].players.length} cầu thủ
                            </span>
                          </div>

                          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                            <div className="overflow-x-auto">
                              <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-100">
                                  <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                                      Số Áo
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                                      Cầu Thủ
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                                      Vị Trí
                                    </th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                  {teamDetails[team.team_id].players.map(
                                    (player) => (
                                      <tr
                                        key={player.roster_id}
                                        className="hover:bg-gray-50"
                                      >
                                        <td className="px-4 py-3">
                                          <span className="inline-flex items-center justify-center w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 text-white font-bold rounded-full text-sm">
                                            {player.shirt_number || "-"}
                                          </span>
                                        </td>
                                        <td className="px-4 py-3">
                                          <div className="flex items-center">
                                            {player.player.image_url ? (
                                              <img
                                                src={player.player.image_url}
                                                alt={player.player.full_name}
                                                className="w-10 h-10 rounded-full object-cover border border-gray-300 mr-3"
                                              />
                                            ) : (
                                              <div className="w-10 h-10 rounded-full bg-gray-200 border border-gray-300 mr-3 flex items-center justify-center">
                                                <Users className="w-5 h-5 text-gray-500" />
                                              </div>
                                            )}
                                            <div>
                                              <div className="font-medium text-gray-900">
                                                {player.player.full_name}
                                              </div>
                                              {player.player.birth_date && (
                                                <div className="text-xs text-gray-500">
                                                  {new Date(
                                                    player.player.birth_date
                                                  ).toLocaleDateString("vi-VN")}
                                                </div>
                                              )}
                                            </div>
                                          </div>
                                        </td>
                                        <td className="px-4 py-3">
                                          <span className="px-2 py-1 inline-flex text-xs font-medium rounded bg-blue-100 text-blue-800">
                                            {player.player.position || "N/A"}
                                          </span>
                                        </td>
                                      </tr>
                                    )
                                  )}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        </div>
                      )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && filteredTeams.length === 0 && (
          <div className="text-center py-16 bg-white rounded-2xl shadow border border-gray-200">
            <Target className="w-16 h-16 mx-auto text-gray-300 mb-6" />
            <h3 className="text-xl font-bold text-gray-700 mb-3">
              Không tìm thấy đội bóng
            </h3>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              {searchTerm
                ? `Không có đội bóng nào phù hợp với "${searchTerm}" trong mùa giải này`
                : "Không có đội bóng nào trong mùa giải này"}
            </p>
            {searchTerm && (
              <button
                onClick={clearSearch}
                className="px-5 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
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

export default Teams;
