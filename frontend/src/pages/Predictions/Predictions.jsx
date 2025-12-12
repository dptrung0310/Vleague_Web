import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  TextField,
  Snackbar,
} from "@mui/material";
import SportsSoccerIcon from "@mui/icons-material/SportsSoccer";
import EventIcon from "@mui/icons-material/Event";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { format } from "date-fns";
import predictionService from "../../services/predictionService";
import "./Predictions.css";

const Predictions = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [predictionDialogOpen, setPredictionDialogOpen] = useState(false);
  const [predictionType, setPredictionType] = useState("result");
  const [predictionData, setPredictionData] = useState({
    predicted_result: "HOME_WIN",
    predicted_home_score: 0,
    predicted_away_score: 0,
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [matchToDelete, setMatchToDelete] = useState(null);

  const fetchUpcomingMatches = async () => {
    try {
      setLoading(true);
      console.log("Fetching ALL upcoming matches...");

      const response = await predictionService.getUpcomingMatches();

      console.log("Full API response:", response);
      console.log("Response data:", response.data);

      // Kiểm tra các cấu trúc có thể có
      let matchesData = [];

      if (response.data) {
        // TH1: response.data.matches
        if (response.data.matches && Array.isArray(response.data.matches)) {
          matchesData = response.data.matches;
          console.log("Found matches in response.data.matches");
        }
        // TH2: response.data.data.matches
        else if (
          response.data.data &&
          response.data.data.matches &&
          Array.isArray(response.data.data.matches)
        ) {
          matchesData = response.data.data.matches;
          console.log("Found matches in response.data.data.matches");
        }
        // TH3: response.matches (nếu axios interceptor trả về data)
        else if (response.matches && Array.isArray(response.matches)) {
          matchesData = response.matches;
          console.log("Found matches in response.matches");
        }

        // Log để debug
        console.log("Final matches data:", matchesData);
        console.log("Number of matches:", matchesData.length);

        if (matchesData.length > 0) {
          // Sắp xếp theo thời gian
          const sortedMatches = [...matchesData].sort((a, b) => {
            const dateA = a.match_datetime
              ? new Date(a.match_datetime)
              : new Date(0);
            const dateB = b.match_datetime
              ? new Date(b.match_datetime)
              : new Date(0);
            return dateA - dateB;
          });

          setMatches(sortedMatches);
          setError(null); // Clear error if successful
        } else {
          setMatches([]);
          setError("No matches found in the response");
        }
      } else {
        setError("Invalid response format");
      }
    } catch (err) {
      console.error("Error in fetchUpcomingMatches:", err);
      console.error("Error details:", {
        message: err.message,
        response: err.response,
        data: err.response?.data,
      });

      setError(
        err.response?.data?.message ||
          "Failed to fetch matches. Please try again."
      );
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUpcomingMatches();
  }, []);

  const handleOpenPredictionDialog = async (match) => {
    try {
      const checkResponse = await predictionService.checkUserPrediction(
        match.match_id
      );

      if (checkResponse.data?.has_predicted || checkResponse?.has_predicted) {
        const prediction =
          checkResponse.data?.prediction || checkResponse?.prediction;

        // QUAN TRỌNG: Xác định loại dự đoán dựa trên tỉ số
        // Nếu tỉ số là null => dự đoán kết quả
        // Nếu tỉ số có giá trị => dự đoán tỉ số
        const hasScorePrediction =
          prediction.predicted_home_score !== null &&
          prediction.predicted_away_score !== null;

        setPredictionType(hasScorePrediction ? "score" : "result");

        // Set dữ liệu
        setPredictionData({
          predicted_result: prediction.predicted_result || "HOME_WIN",
          predicted_home_score: prediction.predicted_home_score || 0,
          predicted_away_score: prediction.predicted_away_score || 0,
        });
      } else {
        // Mặc định là dự đoán kết quả
        setPredictionType("result");
        setPredictionData({
          predicted_result: "HOME_WIN",
          predicted_home_score: 0,
          predicted_away_score: 0,
        });
      }

      setSelectedMatch(match);
      setPredictionDialogOpen(true);
    } catch (err) {
      console.error("Error opening dialog:", err);
      setSnackbar({
        open: true,
        message: "Không thể mở form dự đoán",
        severity: "error",
      });
    }
  };

  const handleClosePredictionDialog = () => {
    // Chỉ đóng dialog nếu không đang submit
    if (!submitting) {
      setPredictionDialogOpen(false);
      // Đợi 100ms rồi reset để tránh conflict
      setTimeout(() => {
        setPredictionType("result");
        setPredictionData({
          predicted_result: "HOME_WIN",
          predicted_home_score: 0,
          predicted_away_score: 0,
        });
        setSelectedMatch(null);
      }, 100);
    }
  };

  useEffect(() => {
    // Reset submitting khi dialog đóng
    if (!predictionDialogOpen) {
      setSubmitting(false);
    }
  }, [predictionDialogOpen]);

  // Thêm debug useEffect
  useEffect(() => {
    console.log("🔍 Matches state updated:", matches.length, "matches");
    console.log("🔍 First match:", matches[0]);
  }, [matches]);

  useEffect(() => {
    console.log("🔍 Selected match:", selectedMatch);
  }, [selectedMatch]);

  const validatePredictionData = () => {
    if (predictionType === "score") {
      // Kiểm tra tỉ số hợp lệ
      const homeScore = predictionData.predicted_home_score;
      const awayScore = predictionData.predicted_away_score;

      if (homeScore < 0 || homeScore > 20 || awayScore < 0 || awayScore > 20) {
        return "Tỉ số phải từ 0 đến 20";
      }

      // Kiểm tra nếu là số âm
      if (homeScore < 0 || awayScore < 0) {
        return "Tỉ số không được âm";
      }
    }
    return null;
  };

  const handlePredictionSubmit = async () => {
    try {
      if (!selectedMatch || submitting) return;
      setSubmitting(true);

      // Validate dữ liệu
      const validationError = validatePredictionData();
      if (validationError) {
        setSnackbar({
          open: true,
          message: validationError,
          severity: "error",
        });
        setSubmitting(false);
        return;
      }

      // Chuẩn bị dữ liệu
      const dataToSend = {
        match_id: selectedMatch.match_id,
        predicted_result: predictionData.predicted_result,
      };

      // QUAN TRỌNG: Chỉ gửi tỉ số khi chọn dự đoán tỉ số
      if (predictionType === "score") {
        dataToSend.predicted_home_score = predictionData.predicted_home_score;
        dataToSend.predicted_away_score = predictionData.predicted_away_score;
      } else {
        // Khi chọn dự đoán kết quả, gửi tỉ số là null
        dataToSend.predicted_home_score = null;
        dataToSend.predicted_away_score = null;
      }

      console.log("📤 Submitting prediction:", {
        type: predictionType,
        data: dataToSend,
      });

      let response;
      let isUpdate = !!selectedMatch.prediction_id;

      try {
        if (isUpdate) {
          console.log("🔄 Updating prediction:", selectedMatch.prediction_id);
          response = await predictionService.updatePrediction(
            selectedMatch.prediction_id,
            dataToSend
          );
        } else {
          console.log("🆕 Creating prediction");
          response = await predictionService.createPrediction(dataToSend);
        }

        console.log("📥 API response:", response);

        // Xử lý response
        const responseData = response.data || response;

        if (
          responseData &&
          (responseData.prediction_id || responseData.match_id)
        ) {
          console.log("✅ Prediction successful");

          // Cập nhật state ngay lập tức - ĐƠN GIẢN HÓA
          const updatedMatches = matches.map((match) => {
            if (match.match_id === selectedMatch.match_id) {
              // Sử dụng toàn bộ dữ liệu từ response
              return {
                ...match,
                prediction_id:
                  responseData.prediction_id || match.prediction_id,
                predicted_result: responseData.predicted_result,
                predicted_home_score: responseData.predicted_home_score,
                predicted_away_score: responseData.predicted_away_score,
              };
            }
            return match;
          });

          setMatches(updatedMatches);

          setSnackbar({
            open: true,
            message: isUpdate
              ? "✅ Cập nhật dự đoán thành công!"
              : "✅ Dự đoán đã được gửi!",
            severity: "success",
          });

          // Đóng dialog
          handleClosePredictionDialog();
        } else {
          console.error("❌ API error:", responseData);
          setSnackbar({
            open: true,
            message: responseData?.message || "Có lỗi xảy ra",
            severity: "error",
          });
        }
      } catch (apiError) {
        console.error("❌ API Error:", apiError);
        setSnackbar({
          open: true,
          message: apiError.response?.data?.message || "Có lỗi xảy ra",
          severity: "error",
        });
      }
    } catch (err) {
      console.error("❌ Unexpected error:", err);
      setSnackbar({
        open: true,
        message: "Lỗi không xác định",
        severity: "error",
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Xử lý xóa dự đoán
  const handleDeleteClick = (match) => {
    setMatchToDelete(match);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!matchToDelete || !matchToDelete.prediction_id) {
      console.error("❌ No prediction_id found in match:", matchToDelete);
      return;
    }

    try {
      console.log("🗑️ Deleting prediction:", {
        prediction_id: matchToDelete.prediction_id,
        match_id: matchToDelete.match_id,
        match_name: `${matchToDelete.home_team_name} vs ${matchToDelete.away_team_name}`,
        current_time: new Date().toISOString(),
        match_time: matchToDelete.match_datetime,
      });

      await predictionService.deletePrediction(matchToDelete.prediction_id);

      // Cập nhật state - xóa thông tin dự đoán
      const updatedMatches = matches.map((match) => {
        if (match.match_id === matchToDelete.match_id) {
          return {
            ...match,
            prediction_id: null,
            predicted_result: null,
            predicted_home_score: null,
            predicted_away_score: null,
          };
        }
        return match;
      });

      setMatches(updatedMatches);

      setSnackbar({
        open: true,
        message: "✅ Đã xóa dự đoán thành công!",
        severity: "success",
      });
    } catch (err) {
      console.error("❌ Error deleting prediction:", err);
      console.error("❌ Error response data:", err.response?.data);
      console.error("❌ Error status:", err.response?.status);

      setSnackbar({
        open: true,
        message: err.response?.data?.message || "❌ Không thể xóa dự đoán",
        severity: "error",
      });
    } finally {
      setDeleteConfirmOpen(false);
      setMatchToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmOpen(false);
    setMatchToDelete(null);
  };

  const handlePredictionTypeChange = (event) => {
    setPredictionType(event.target.value);
  };

  const handleResultChange = (event) => {
    setPredictionData({
      ...predictionData,
      predicted_result: event.target.value,
    });
  };

  const handleScoreChange = (field) => (event) => {
    const value = parseInt(event.target.value) || 0;
    if (value >= 0 && value <= 20) {
      setPredictionData({
        ...predictionData,
        [field]: value,
      });
    }
  };

  const getResultLabel = (result) => {
    switch (result) {
      case "HOME_WIN":
        return `${selectedMatch?.home_team_name} Thắng`;
      case "AWAY_WIN":
        return `${selectedMatch?.away_team_name} Thắng`;
      case "DRAW":
        return "Hòa";
      default:
        return "Chưa chọn";
    }
  };

  if (loading) {
    return (
      <Container
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "50vh",
        }}
      >
        <Box sx={{ textAlign: "center" }}>
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            Đang tải trận đấu...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography
        variant="h4"
        component="h1"
        gutterBottom
        sx={{ fontWeight: "bold" }}
      >
        <EmojiEventsIcon sx={{ mr: 1, verticalAlign: "middle" }} />
        Dự Đoán Trận Đấu
      </Typography>

      {error && (
        <Alert
          severity="error"
          sx={{ mb: 2 }}
          action={
            <Button color="inherit" size="small" onClick={fetchUpcomingMatches}>
              Thử lại
            </Button>
          }
        >
          {error}
        </Alert>
      )}

      <Typography variant="body1" color="text.secondary" paragraph>
        Dự đoán kết quả các trận đấu sắp diễn ra và kiếm điểm cho những dự đoán
        chính xác!
        {matches.length > 0 && ` Có ${matches.length} trận đấu sắp diễn ra.`}
      </Typography>

      {matches.length === 0 && !error ? (
        <Alert severity="info" sx={{ mt: 2 }}>
          Hiện không có trận đấu nào sắp diễn ra để dự đoán.
          <br />
          <Typography variant="caption">
            Điều này có thể do:
            <ul style={{ margin: 0, paddingLeft: "20px" }}>
              <li>Tất cả trận đấu đã kết thúc</li>
              <li>Chưa có trận đấu nào trong mùa giải hiện tại</li>
              <li>Có lỗi khi tải dữ liệu</li>
            </ul>
          </Typography>
        </Alert>
      ) : (
        <>
          {matches.length > 0 && (
            <Typography variant="subtitle1" color="primary" sx={{ mb: 2 }}>
              📋 Đang hiển thị {matches.length} trận đấu sắp diễn ra
            </Typography>
          )}

          <Grid container spacing={3}>
            {matches.map((match) => (
              <Grid item xs={12} sm={6} md={4} key={match.match_id || match.id}>
                <Card
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    transition: "transform 0.2s",
                    "&:hover": {
                      transform: "translateY(-4px)",
                      boxShadow: 6,
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 2,
                      }}
                    >
                      <Chip
                        icon={<EventIcon />}
                        label={
                          match.match_datetime
                            ? format(
                                new Date(match.match_datetime),
                                "dd/MM • HH:mm"
                              )
                            : "Chưa xác định"
                        }
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      {match.prediction_id && (
                        <Chip label="Đã dự đoán" color="success" size="small" />
                      )}
                    </Box>

                    <Box sx={{ textAlign: "center", mb: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        {match.round || "Trận đấu"}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 1 }}
                      >
                        <LocationOnIcon sx={{ fontSize: 14, mr: 0.5 }} />
                        {match.stadium_name || "Sân vận động"}
                      </Typography>
                    </Box>

                    {/* Teams Display */}
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        mb: 2,
                      }}
                    >
                      {/* Đội nhà */}
                      <Box sx={{ textAlign: "center", flex: 1 }}>
                        {match.home_team_logo ? (
                          <img
                            src={match.home_team_logo}
                            alt={match.home_team_name}
                            style={{
                              width: 60,
                              height: 60,
                              objectFit: "contain",
                            }}
                          />
                        ) : (
                          <SportsSoccerIcon
                            sx={{ fontSize: 60, color: "primary.main" }}
                          />
                        )}
                        <Typography
                          variant="subtitle1"
                          sx={{ mt: 1, fontWeight: "bold" }}
                        >
                          {match.home_team_name || "Đội nhà"}
                        </Typography>
                      </Box>

                      <Box sx={{ mx: 2, textAlign: "center" }}>
                        <Typography
                          variant="h5"
                          sx={{ fontWeight: "bold", color: "text.secondary" }}
                        >
                          VS
                        </Typography>
                        <Typography
                          variant="caption"
                          display="block"
                          color="text.secondary"
                        >
                          {match.match_datetime
                            ? format(new Date(match.match_datetime), "HH:mm")
                            : ""}
                        </Typography>
                      </Box>

                      {/* Đội khách */}
                      <Box sx={{ textAlign: "center", flex: 1 }}>
                        {match.away_team_logo ? (
                          <img
                            src={match.away_team_logo}
                            alt={match.away_team_name}
                            style={{
                              width: 60,
                              height: 60,
                              objectFit: "contain",
                            }}
                          />
                        ) : (
                          <SportsSoccerIcon
                            sx={{ fontSize: 60, color: "secondary.main" }}
                          />
                        )}
                        <Typography
                          variant="subtitle1"
                          sx={{ mt: 1, fontWeight: "bold" }}
                        >
                          {match.away_team_name || "Đội khách"}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Dự đoán của user (nếu có) */}
                    {match.prediction_id && (
                      <Box
                        sx={{
                          mt: 2,
                          p: 2,
                          bgcolor: "success.light",
                          borderRadius: 1,
                          border: "1px solid",
                          borderColor: "success.main",
                        }}
                      >
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: "bold",
                            color: "success.dark",
                            mb: 0.5,
                          }}
                        >
                          ⚽ Dự đoán của bạn
                        </Typography>

                        {/* LOGIC HIỂN THỊ MỚI */}
                        {match.predicted_home_score !== null &&
                        match.predicted_away_score !== null ? (
                          // Có tỉ số: Hiển thị tỉ số
                          <Typography variant="body2" color="success.dark">
                            Tỉ số: {match.predicted_home_score} -{" "}
                            {match.predicted_away_score}
                          </Typography>
                        ) : (
                          // Không có tỉ số (null): Hiển thị kết quả
                          <Typography variant="body2" color="success.dark">
                            {match.predicted_result === "HOME_WIN"
                              ? `${match.home_team_name} Thắng`
                              : match.predicted_result === "AWAY_WIN"
                              ? `${match.away_team_name} Thắng`
                              : "Hòa"}
                          </Typography>
                        )}
                      </Box>
                    )}
                  </CardContent>

                  <CardActions sx={{ p: 2, pt: 0 }}>
                    {match.prediction_id ? (
                      // Khi đã có dự đoán: Hiển thị 2 nút Sửa và Xóa
                      <Box sx={{ display: "flex", gap: 1, width: "100%" }}>
                        <Button
                          variant="outlined"
                          color="secondary"
                          onClick={() => handleOpenPredictionDialog(match)}
                          startIcon={<EditIcon />}
                          sx={{ flex: 1 }}
                        >
                          Sửa dự đoán
                        </Button>
                        <Button
                          variant="outlined"
                          color="error"
                          onClick={() => handleDeleteClick(match)}
                          startIcon={<DeleteIcon />}
                          sx={{ flex: 1 }}
                        >
                          Xóa dự đoán
                        </Button>
                      </Box>
                    ) : (
                      // Khi chưa có dự đoán: Hiển thị 1 nút lớn
                      <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        onClick={() => handleOpenPredictionDialog(match)}
                        startIcon={<EmojiEventsIcon />}
                      >
                        Dự đoán ngay
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      {/* Dialog dự đoán */}
      <Dialog
        open={predictionDialogOpen}
        onClose={handleClosePredictionDialog}
        maxWidth="sm"
        fullWidth
        disableEnforceFocus
      >
        <DialogTitle>
          {selectedMatch?.prediction_id ? "Sửa dự đoán" : "Dự đoán kết quả"}
        </DialogTitle>
        <DialogContent>
          {selectedMatch && (
            <>
              <Box sx={{ textAlign: "center", mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {selectedMatch.home_team_name} vs{" "}
                  {selectedMatch.away_team_name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedMatch.match_datetime
                    ? format(
                        new Date(selectedMatch.match_datetime),
                        "dd/MM/yyyy • HH:mm"
                      )
                    : "Chưa xác định"}
                </Typography>
                {selectedMatch.round && (
                  <Typography
                    variant="caption"
                    display="block"
                    color="text.secondary"
                  >
                    {selectedMatch.round}
                  </Typography>
                )}
              </Box>

              {/* Thông báo loại dự đoán */}
              <Alert
                severity="info"
                sx={{ mb: 2 }}
                icon={
                  predictionType === "score" ? (
                    <EditIcon />
                  ) : (
                    <EmojiEventsIcon />
                  )
                }
              >
                <Typography variant="body2">
                  {predictionType === "score"
                    ? "Bạn đang dự đoán tỉ số. Chỉ hiển thị tỉ số trên thẻ."
                    : 'Bạn đang dự đoán kết quả. Chỉ hiển thị "Thắng/Hòa/Thua" trên thẻ.'}
                </Typography>
              </Alert>

              <FormControl component="fieldset" sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Loại dự đoán
                </Typography>
                <RadioGroup
                  row
                  value={predictionType}
                  onChange={handlePredictionTypeChange}
                >
                  <FormControlLabel
                    value="result"
                    control={<Radio />}
                    label="Thắng/Hòa/Thua"
                  />
                  <FormControlLabel
                    value="score"
                    control={<Radio />}
                    label="Tỉ số chính xác"
                  />
                </RadioGroup>
              </FormControl>

              {predictionType === "result" ? (
                <FormControl component="fieldset" sx={{ width: "100%" }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Chọn kết quả
                  </Typography>
                  <RadioGroup
                    value={predictionData.predicted_result}
                    onChange={handleResultChange}
                  >
                    <FormControlLabel
                      value="HOME_WIN"
                      control={<Radio />}
                      label={`${selectedMatch.home_team_name} Thắng`}
                    />
                    <FormControlLabel
                      value="DRAW"
                      control={<Radio />}
                      label="Hòa"
                    />
                    <FormControlLabel
                      value="AWAY_WIN"
                      control={<Radio />}
                      label={`${selectedMatch.away_team_name} Thắng`}
                    />
                  </RadioGroup>
                </FormControl>
              ) : (
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <Box sx={{ flex: 1, textAlign: "center" }}>
                    <Typography variant="body2" gutterBottom>
                      {selectedMatch.home_team_name}
                    </Typography>
                    <TextField
                      type="number"
                      value={predictionData.predicted_home_score}
                      onChange={handleScoreChange("predicted_home_score")}
                      inputProps={{ min: 0, max: 20 }}
                      variant="outlined"
                      size="small"
                      fullWidth
                    />
                  </Box>

                  <Typography variant="h5">-</Typography>

                  <Box sx={{ flex: 1, textAlign: "center" }}>
                    <Typography variant="body2" gutterBottom>
                      {selectedMatch.away_team_name}
                    </Typography>
                    <TextField
                      type="number"
                      value={predictionData.predicted_away_score}
                      onChange={handleScoreChange("predicted_away_score")}
                      inputProps={{ min: 0, max: 20 }}
                      variant="outlined"
                      size="small"
                      fullWidth
                    />
                  </Box>
                </Box>
              )}

              <Box sx={{ mt: 3, p: 2, bgcolor: "info.light", borderRadius: 1 }}>
                <Typography variant="caption">
                  <strong>Lưu ý:</strong> Bạn có thể thay đổi dự đoán cho đến
                  khi trận đấu bắt đầu. Điểm thưởng được tính như sau:
                  <ul style={{ margin: 0, paddingLeft: 16 }}>
                    <li>Dự đoán đúng kết quả: 3 điểm</li>
                    <li>Dự đoán đúng tỉ số: 5 điểm (thêm)</li>
                    <li>Sai lệch 1 bàn: 2 điểm (thêm)</li>
                  </ul>
                </Typography>
              </Box>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePredictionDialog} disabled={submitting}>
            Hủy
          </Button>
          <Button
            onClick={handlePredictionSubmit}
            variant="contained"
            color="primary"
            disabled={submitting}
            startIcon={submitting ? <CircularProgress size={20} /> : null}
          >
            {submitting
              ? "Đang xử lý..."
              : selectedMatch?.prediction_id
              ? "Cập nhật"
              : "Gửi dự đoán"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog xác nhận xóa */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={handleDeleteCancel}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Xác nhận xóa dự đoán</DialogTitle>
        <DialogContent>
          <Typography>
            Bạn có chắc chắn muốn xóa dự đoán này không?
            <br />
            <strong>Hành động này không thể hoàn tác.</strong>
          </Typography>
          {matchToDelete && (
            <Box sx={{ mt: 2, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
              <Typography variant="body2">
                <strong>Trận đấu:</strong> {matchToDelete.home_team_name} vs{" "}
                {matchToDelete.away_team_name}
                <br />
                <strong>Thời gian:</strong>{" "}
                {matchToDelete.match_datetime
                  ? format(
                      new Date(matchToDelete.match_datetime),
                      "dd/MM/yyyy HH:mm"
                    )
                  : "Chưa xác định"}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Hủy</Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
          >
            Xóa dự đoán
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar thông báo */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Predictions;
