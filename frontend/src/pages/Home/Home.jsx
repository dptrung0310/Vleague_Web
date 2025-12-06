// src/pages/Home.jsx
import React, { useEffect, useState } from "react";
import matchService from "../../services/matchService";
import seasonService from "../../services/seasonService";
import MatchPost from "../../components/MatchPost";
import MatchModal from "../../components/MatchModal";
import {
  Calendar,
  Trophy,
  Filter,
  ChevronDown,
  Search,
  X,
  Loader,
} from "lucide-react";

const Home = () => {
  const [matches, setMatches] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState(null);

  // State cho bộ lọc - THÊM loadingSeasons
  const [seasons, setSeasons] = useState([]);
  const [loadingSeasons, setLoadingSeasons] = useState(true); // Thêm state này
  const [selectedSeason, setSelectedSeason] = useState("");
  const [roundFilter, setRoundFilter] = useState("");
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  // Lấy danh sách mùa giải
  useEffect(() => {
    const fetchSeasons = async () => {
      setLoadingSeasons(true);
      try {
        const response = await seasonService.getAllSeasons();
        if (response.status === "success") {
          setSeasons(response.data || []);

          // Nếu có dữ liệu, tự động chọn mùa giải hiện tại (mới nhất)
          if (response.data && response.data.length > 0) {
            // Mùa đầu tiên trong danh sách (đã sắp xếp mới nhất trước)
            const currentSeason = response.data[0];
            setSelectedSeason(currentSeason.season_id.toString());
          }
        } else {
          // Fallback data nếu API trả về lỗi
          setSeasons([
            { season_id: 1, name: "V-League 2024/25", vpf_sid: 12345 },
            { season_id: 2, name: "V-League 2023/24", vpf_sid: 12344 },
          ]);
        }
      } catch (error) {
        console.error("Lỗi tải mùa giải:", error);
        // Fallback data khi API lỗi
        setSeasons([
          { season_id: 1, name: "V-League 2024/25", vpf_sid: 12345 },
          { season_id: 2, name: "V-League 2023/24", vpf_sid: 12344 },
          { season_id: 3, name: "V-League 2022/23", vpf_sid: 12343 },
          { season_id: 4, name: "V-League 2021/22", vpf_sid: 12342 },
        ]);
      } finally {
        setLoadingSeasons(false);
      }
    };
    fetchSeasons();
  }, []);

  // Lấy trận đấu với bộ lọc
  const loadMatches = async (pageNumber = 1, reset = false) => {
    if (reset) {
      setLoading(true);
      setPage(1);
    } else {
      setLoadingMore(true);
    }

    try {
      const params = {
        page: pageNumber,
        per_page: 12,
        status: "Kết thúc",
      };

      // Thêm bộ lọc nếu có
      if (selectedSeason) {
        params.season_id = selectedSeason;
      }
      if (roundFilter) {
        params.round = roundFilter;
      }

      const response = await matchService.getAllMatches(params);

      if (response.status === "success") {
        const newMatches = response.data || [];
        const hasNext = response.has_next;

        if (reset || pageNumber === 1) {
          setMatches(newMatches);
        } else {
          setMatches((prev) => [...prev, ...newMatches]);
        }

        setHasMore(hasNext);
        if (hasNext) {
          setPage(pageNumber + 1);
        }
      }
    } catch (error) {
      console.error("Lỗi tải trận đấu:", error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  // Load trận đấu đầu tiên
  useEffect(() => {
    if (!loadingSeasons) {
      // Chỉ load matches khi đã tải xong seasons
      loadMatches(1, true);
    }
  }, [selectedSeason, roundFilter, loadingSeasons]); // Thêm loadingSeasons vào dependency

  const handleLoadMore = () => {
    loadMatches(page, false);
  };

  const clearFilters = () => {
    setSelectedSeason("");
    setRoundFilter("");
  };

  const getFilterCount = () => {
    let count = 0;
    if (selectedSeason) count++;
    if (roundFilter) count++;
    return count;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white">
        <div className="container mx-auto px-4 py-12 md:py-16">
          <div className="max-w-3xl">
            <div className="flex items-center gap-3 mb-4">
              <Trophy className="w-8 h-8" />
              <span className="text-sm font-semibold uppercase tracking-wider bg-white/20 px-3 py-1 rounded-full">
                V-League Stats
              </span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Kết quả bóng đá V-League
            </h1>
            <p className="text-lg text-blue-100 mb-6">
              Cập nhật tỷ số và thông tin chi tiết các trận đấu đã kết thúc
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Feed - 3/4 width on desktop */}
          <div className="lg:col-span-3">
            {/* Filter Bar */}
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">
                    Trận đấu đã kết thúc
                  </h2>
                  <p className="text-gray-600 mt-1">
                    Xem kết quả và thống kê chi tiết
                  </p>
                </div>

                {/* Filter Button (Mobile) */}
                <button
                  onClick={() => setIsFilterOpen(!isFilterOpen)}
                  className="md:hidden flex items-center gap-2 px-4 py-3 bg-blue-50 text-blue-700 rounded-xl font-medium"
                >
                  <Filter className="w-5 h-5" />
                  Bộ lọc
                  {getFilterCount() > 0 && (
                    <span className="bg-blue-600 text-white text-xs w-6 h-6 rounded-full flex items-center justify-center">
                      {getFilterCount()}
                    </span>
                  )}
                  <ChevronDown
                    className={`w-4 h-4 transition-transform ${
                      isFilterOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>
              </div>

              {/* Filter Content */}
              <div
                className={`${isFilterOpen ? "block" : "hidden md:block"} mt-6`}
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Season Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Mùa giải
                    </label>
                    <div className="relative">
                      {loadingSeasons ? (
                        <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl">
                          <Loader className="w-5 h-5 animate-spin text-gray-400" />
                          <span className="text-gray-500">
                            Đang tải mùa giải...
                          </span>
                        </div>
                      ) : (
                        <>
                          <select
                            value={selectedSeason}
                            onChange={(e) => setSelectedSeason(e.target.value)}
                            className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none text-gray-900"
                          >
                            <option value="">Tất cả mùa giải</option>
                            {seasons.map((season) => (
                              <option
                                key={season.season_id}
                                value={season.season_id}
                                className="text-gray-900 py-2"
                              >
                                {season.name}
                              </option>
                            ))}
                          </select>
                          <ChevronDown className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                        </>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {selectedSeason
                        ? `Đã chọn: ${
                            seasons.find(
                              (s) => s.season_id.toString() === selectedSeason
                            )?.name || ""
                          }`
                        : "Chọn mùa giải để lọc"}
                    </p>
                  </div>

                  {/* Round Filter */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Vòng đấu
                    </label>
                    <div className="relative">
                      <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
                        <Search className="w-5 h-5 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        placeholder="VD: 26, 1, 10"
                        value={roundFilter}
                        onChange={(e) => setRoundFilter(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-500"
                      />
                      {roundFilter && (
                        <button
                          onClick={() => setRoundFilter("")}
                          className="absolute right-4 top-1/2 transform -translate-y-1/2"
                          type="button"
                        >
                          <X className="w-5 h-5 text-gray-400 hover:text-gray-600" />
                        </button>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Nhập số vòng đấu cụ thể
                    </p>
                  </div>
                </div>

                {/* Clear Filters */}
                {(selectedSeason || roundFilter) && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <button
                      onClick={clearFilters}
                      className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
                      type="button"
                    >
                      <X className="w-4 h-4" />
                      Xóa tất cả bộ lọc
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Loading State */}
            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600">Đang tải trận đấu...</p>
              </div>
            ) : (
              <>
                {/* Matches Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {matches.length === 0 ? (
                    <div className="col-span-2 text-center py-12">
                      <div className="max-w-md mx-auto">
                        <div className="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                          <Trophy className="w-12 h-12 text-gray-400" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2">
                          Không có trận đấu nào
                        </h3>
                        <p className="text-gray-500">
                          Không tìm thấy trận đấu nào phù hợp với bộ lọc của
                          bạn.
                        </p>
                      </div>
                    </div>
                  ) : (
                    matches.map((match) => (
                      <div
                        key={match.match_id}
                        className="transform transition-transform hover:-translate-y-1"
                      >
                        <MatchPost match={match} onClick={setSelectedMatch} />
                      </div>
                    ))
                  )}
                </div>

                {/* Load More Button */}
                {hasMore && matches.length > 0 && (
                  <div className="text-center mt-12">
                    <button
                      onClick={handleLoadMore}
                      disabled={loadingMore}
                      className="inline-flex items-center gap-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-4 px-8 rounded-xl shadow-lg hover:shadow-xl hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loadingMore ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          Đang tải...
                        </>
                      ) : (
                        <>
                          Xem thêm trận đấu
                          <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 9l-7 7-7-7"
                            />
                          </svg>
                        </>
                      )}
                    </button>
                    <p className="text-sm text-gray-500 mt-4">
                      Hiển thị {matches.length} trận đấu
                    </p>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Stats Card */}
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Trophy className="w-5 h-5 text-blue-600" />
                Thống kê
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Đang hiển thị</span>
                  <span className="font-bold text-blue-600">
                    {matches.length}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Mùa giải</span>
                  <span className="font-bold text-green-600">
                    {selectedSeason
                      ? seasons
                          .find(
                            (s) => s.season_id.toString() === selectedSeason
                          )
                          ?.name.split(" ")
                          .pop() || "N/A"
                      : "Tất cả"}
                  </span>
                </div>
                {roundFilter && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Vòng đấu</span>
                    <span className="font-bold text-orange-600">
                      {roundFilter}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Season Info */}
            {selectedSeason && (
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-3">
                  Mùa giải đã chọn
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    {
                      seasons.find(
                        (s) => s.season_id.toString() === selectedSeason
                      )?.name
                    }
                  </p>
                  <p className="text-xs text-gray-500">
                    Bộ lọc đang được áp dụng
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal chi tiết */}
      {selectedMatch && (
        <MatchModal
          match={selectedMatch}
          onClose={() => setSelectedMatch(null)}
        />
      )}
    </div>
  );
};

export default Home;
