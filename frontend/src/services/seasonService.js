// src/services/seasonService.js
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const seasonService = {
  getAllSeasons: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/seasons`);
      return response.data;
    } catch (error) {
      console.error("Error fetching seasons:", error);
      throw error;
    }
  },
};

export default seasonService;
