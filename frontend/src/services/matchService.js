// src/services/matchService.js
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const matchService = {
  getAllMatches: async (params = {}) => {
    try {
      console.log("Fetching matches with params:", params);
      const response = await axios.get(`${API_BASE_URL}/matches`, { params });
      console.log("Matches response:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error fetching matches:", error);
      throw error;
    }
  },

  getMatchDetails: async (matchId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/matches/${matchId}/details`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching match details ${matchId}:`, error);
      throw error;
    }
  },

  getMatchById: async (matchId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/matches/${matchId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching match ${matchId}:`, error);
      throw error;
    }
  },

  getMatchesByTeam: async (teamId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/matches/team/${teamId}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching matches for team ${teamId}:`, error);
      throw error;
    }
  },

  getMatchesBySeason: async (seasonId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/matches`, {
        params: { season_id: seasonId },
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching matches for season ${seasonId}:`, error);
      throw error;
    }
  },

  getMatchesByRound: async (round) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/matches`, {
        params: { round: round },
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching matches for round ${round}:`, error);
      throw error;
    }
  },
};

export default matchService;
