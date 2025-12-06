// src/services/teamService.js
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

console.log("API Base URL:", API_BASE_URL); // Debug

const teamService = {
  // Lấy danh sách đội theo mùa
  getTeamsBySeason: async (seasonId) => {
    try {
      console.log(
        `Fetching teams for season ${seasonId} from ${API_BASE_URL}/teams/season/${seasonId}`
      );

      const response = await axios.get(
        `${API_BASE_URL}/teams/season/${seasonId}`
      );

      console.log(`Response status: ${response.status}`);
      console.log(`Response data:`, response.data);

      return response.data;
    } catch (error) {
      console.error(`Error fetching teams for season ${seasonId}:`, error);
      console.error(`Error details:`, {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        url: error.config?.url,
      });

      // Trả về dữ liệu mẫu để test nếu API lỗi
      return {
        status: "success",
        data: [
          {
            team_id: 1,
            name: "Hà Nội FC",
            logo_url: "https://example.com/hanoi.png",
            home_stadium: {
              name: "Sân Hàng Đẫy",
              city: "Hà Nội",
            },
            standing: {
              position: 1,
              played: 26,
              wins: 18,
              draws: 5,
              losses: 3,
              goals_for: 58,
              goals_against: 22,
              goal_difference: 36,
              points: 59,
            },
          },
          {
            team_id: 2,
            name: "Hoàng Anh Gia Lai",
            logo_url: "https://example.com/hagl.png",
            home_stadium: {
              name: "Sân Pleiku",
              city: "Gia Lai",
            },
            standing: {
              position: 2,
              played: 26,
              wins: 15,
              draws: 7,
              losses: 4,
              goals_for: 47,
              goals_against: 25,
              goal_difference: 22,
              points: 52,
            },
          },
        ],
      };
    }
  },

  // Lấy chi tiết đội trong mùa
  getTeamSeasonDetails: async (teamId, seasonId) => {
    try {
      console.log(`Fetching team ${teamId} details for season ${seasonId}`);

      const response = await axios.get(
        `${API_BASE_URL}/teams/${teamId}/season/${seasonId}`
      );

      console.log(`Team details response:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching team ${teamId} details:`, error);

      // Trả về dữ liệu mẫu để test
      return {
        status: "success",
        data: {
          team_id: teamId,
          name: teamId === 1 ? "Hà Nội FC" : "Hoàng Anh Gia Lai",
          logo_url: `https://example.com/team${teamId}.png`,
          standing: {
            position: teamId === 1 ? 1 : 2,
            played: 26,
            wins: teamId === 1 ? 18 : 15,
            draws: 5,
            losses: 3,
            goals_for: teamId === 1 ? 58 : 47,
            goals_against: 22,
            goal_difference: teamId === 1 ? 36 : 25,
            points: teamId === 1 ? 59 : 52,
          },
          players: [
            {
              roster_id: 1,
              shirt_number: 1,
              player: {
                player_id: 1,
                full_name: "Nguyễn Văn Hoàng",
                birth_date: "1990-05-20",
                height_cm: 185,
                weight_kg: 78,
                position: "Thủ môn",
                image_url: "https://example.com/player1.png",
              },
            },
            {
              roster_id: 2,
              shirt_number: 10,
              player: {
                player_id: 2,
                full_name: "Nguyễn Quang Hải",
                birth_date: "1997-04-12",
                height_cm: 168,
                weight_kg: 65,
                position: "Tiền vệ",
                image_url: "https://example.com/player2.png",
              },
            },
          ],
        },
      };
    }
  },

  // Lấy tất cả đội bóng
  getAllTeams: async (includeStadium = false) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/teams`, {
        params: { include_stadium: includeStadium },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching teams:", error);
      throw error;
    }
  },

  // Lấy đội bóng theo ID
  getTeamById: async (teamId, includeStadium = false) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/teams/${teamId}`, {
        params: { include_stadium: includeStadium },
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching team ${teamId}:`, error);
      throw error;
    }
  },

  // Tìm kiếm đội bóng
  searchTeams: async (name = null, city = null) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/teams`, {
        params: { name, city },
      });
      return response.data;
    } catch (error) {
      console.error("Error searching teams:", error);
      throw error;
    }
  },
};

export default teamService;
