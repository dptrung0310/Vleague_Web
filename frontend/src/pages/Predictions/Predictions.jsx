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
import LockIcon from "@mui/icons-material/Lock"; // Icon ổ khóa
import FlagIcon from "@mui/icons-material/Flag"; // Icon thẻ phạt
import { format } from "date-fns";
import predictionService from "../../services/predictionService";
import "./Predictions.css";

const Predictions = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [predictionDialogOpen, setPredictionDialogOpen] = useState(false);

  // State quản lý loại dự đoán
  const [predictionType, setPredictionType] = useState("result");
  const [predictionData, setPredictionData] = useState({
    predicted_result: "HOME_WIN",
    predicted_home_score: 0,
    predicted_away_score: 0,
    predicted_card_over_under: "OVER_3.5",
  });

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [matchToDelete, setMatchToDelete] = useState(null);

  // --- 1. LẤY DANH SÁCH TRẬN ĐẤU ---
  const fetchUpcomingMatches = async () => {
    try {
      setLoading(true);
      const response = await predictionService.getUpcomingMatches();
      let matchesData = [];

      if (response.data) {
        if (response.data.matches && Array.isArray(response.data.matches)) {
          matchesData = response.data.matches;
        } else if (response.data.data && response.data.data.matches) {
          matchesData = response.data.data.matches;
        }

        if (matchesData.length > 0) {
          // Sắp xếp: Ưu tiên "Đang diễn ra" lên đầu, sau đó đến thời gian
          const sortedMatches = [...matchesData].sort((a, b) => {
            if (a.status === "Đang diễn ra" && b.status !== "Đang diễn ra")
              return -1;
            if (a.status !== "Đang diễn ra" && b.status === "Đang diễn ra")
              return 1;
            const dateA = a.match_datetime
              ? new Date(a.match_datetime)
              : new Date(0);
            const dateB = b.match_datetime
              ? new Date(b.match_datetime)
              : new Date(0);
            return dateA - dateB;
          });

          setMatches(sortedMatches);
          setError(null);
        } else {
          setMatches([]);
        }
      }
    } catch (err) {
      console.error("Error fetching matches:", err);
      setError("Không thể tải danh sách trận đấu.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUpcomingMatches();
  }, []);

  // --- 2. XỬ LÝ MỞ FORM DỰ ĐOÁN ---
  const handleOpenPredictionDialog = async (match) => {
    // Nếu trận đấu đã bắt đầu (không phải 'Chưa đá'), chặn không cho mở form
    if (match.status !== "Chưa đá") {
      setSnackbar({
        open: true,
        message: "Trận đấu đã bắt đầu, không thể dự đoán!",
        severity: "warning",
      });
      return;
    }

    try {
      const checkResponse = await predictionService.checkUserPrediction(
        match.match_id
      );

      if (checkResponse.data?.has_predicted || checkResponse?.has_predicted) {
        const prediction =
          checkResponse.data?.prediction || checkResponse?.prediction;

        // Tự động xác định loại dự đoán cũ để hiển thị đúng tab
        let type = "result";
        if (prediction.predicted_card_over_under) {
          type = "cards";
        } else if (prediction.predicted_home_score !== null) {
          type = "score";
        }

        setPredictionType(type);
        setPredictionData({
          predicted_result: prediction.predicted_result || "HOME_WIN",
          predicted_home_score: prediction.predicted_home_score || 0,
          predicted_away_score: prediction.predicted_away_score || 0,
          predicted_card_over_under:
            prediction.predicted_card_over_under || "OVER_3.5",
        });
      } else {
        // Mặc định nếu chưa dự đoán
        setPredictionType("result");
        setPredictionData({
          predicted_result: "HOME_WIN",
          predicted_home_score: 0,
          predicted_away_score: 0,
          predicted_card_over_under: "OVER_3.5",
        });
      }
      setSelectedMatch(match);
      setPredictionDialogOpen(true);
    } catch (err) {
      console.error(err);
      setSnackbar({ open: true, message: "Lỗi mở form", severity: "error" });
    }
  };

  const handleClosePredictionDialog = () => {
    if (!submitting) {
      setPredictionDialogOpen(false);
      setTimeout(() => setSelectedMatch(null), 100);
    }
  };

  // --- 3. XỬ LÝ INPUT ---
  const handlePredictionTypeChange = (event) =>
    setPredictionType(event.target.value);
  const handleResultChange = (event) =>
    setPredictionData({
      ...predictionData,
      predicted_result: event.target.value,
    });
  const handleCardChange = (event) =>
    setPredictionData({
      ...predictionData,
      predicted_card_over_under: event.target.value,
    });
  const handleScoreChange = (field) => (event) => {
    const value = parseInt(event.target.value) || 0;
    if (value >= 0 && value <= 20)
      setPredictionData({ ...predictionData, [field]: value });
  };

  // --- 4. GỬI DỰ ĐOÁN (SUBMIT) ---
  const handlePredictionSubmit = async () => {
    if (!selectedMatch || submitting) return;
    setSubmitting(true);

    const dataToSend = {
      match_id: selectedMatch.match_id,
      predicted_result:
        predictionType === "result" ? predictionData.predicted_result : null,
      predicted_home_score:
        predictionType === "score" ? predictionData.predicted_home_score : null,
      predicted_away_score:
        predictionType === "score" ? predictionData.predicted_away_score : null,
      predicted_card_over_under:
        predictionType === "cards"
          ? predictionData.predicted_card_over_under
          : null,
    };

    try {
      let response;
      const isUpdate = !!selectedMatch.prediction_id;
      if (isUpdate) {
        response = await predictionService.updatePrediction(
          selectedMatch.prediction_id,
          dataToSend
        );
      } else {
        response = await predictionService.createPrediction(dataToSend);
      }

      const responseData = response.data || response;

      // Cập nhật lại UI ngay lập tức mà không cần reload
      const updatedMatches = matches.map((match) => {
        if (match.match_id === selectedMatch.match_id) {
          return {
            ...match,
            prediction_id:
              responseData.prediction_id ||
              responseData.data?.prediction_id ||
              match.prediction_id,
            predicted_result: dataToSend.predicted_result,
            predicted_home_score: dataToSend.predicted_home_score,
            predicted_away_score: dataToSend.predicted_away_score,
            predicted_card_over_under: dataToSend.predicted_card_over_under,
          };
        }
        return match;
      });

      setMatches(updatedMatches);
      setSnackbar({
        open: true,
        message: isUpdate ? "Cập nhật thành công!" : "Dự đoán thành công!",
        severity: "success",
      });
      handleClosePredictionDialog();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.message || "Có lỗi xảy ra",
        severity: "error",
      });
    } finally {
      setSubmitting(false);
    }
  };

  // --- 5. XÓA DỰ ĐOÁN ---
  const handleDeleteClick = (match) => {
    setMatchToDelete(match);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!matchToDelete?.prediction_id) return;
    try {
      await predictionService.deletePrediction(matchToDelete.prediction_id);

      const updatedMatches = matches.map((m) => {
        if (m.match_id === matchToDelete.match_id) {
          return {
            ...m,
            prediction_id: null,
            predicted_result: null,
            predicted_home_score: null,
            predicted_away_score: null,
            predicted_card_over_under: null,
          };
        }
        return m;
      });
      setMatches(updatedMatches);
      setSnackbar({
        open: true,
        message: "Đã xóa dự đoán",
        severity: "success",
      });
    } catch (err) {
      setSnackbar({ open: true, message: "Lỗi khi xóa", severity: "error" });
    } finally {
      setDeleteConfirmOpen(false);
      setMatchToDelete(null);
    }
  };

  // Helper render trạng thái trận đấu
  const renderMatchStatus = (match) => {
    if (match.status === "Đang diễn ra") {
      return (
        <Chip
          label="LIVE"
          color="error"
          size="small"
          sx={{
            fontWeight: "bold",
            animation: "pulse 1.5s infinite",
            "@keyframes pulse": {
              "0%": { opacity: 1 },
              "50%": { opacity: 0.5 },
              "100%": { opacity: 1 },
            },
          }}
        />
      );
    }
    return (
      <Chip
        icon={<EventIcon />}
        label={
          match.match_datetime
            ? format(new Date(match.match_datetime), "dd/MM HH:mm")
            : "Chưa xếp lịch"
        }
        size="small"
        color="primary"
        variant="outlined"
      />
    );
  };

  if (loading)
    return (
      <Container sx={{ mt: 5, textAlign: "center" }}>
        <CircularProgress />
      </Container>
    );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: "bold" }}>
        <EmojiEventsIcon sx={{ mr: 1, verticalAlign: "bottom" }} />
        Dự Đoán Trận Đấu
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}

      {matches.length === 0 && !error ? (
        <Alert severity="info" sx={{ mt: 2 }}>
          Hiện không có trận đấu nào sắp diễn ra.
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {matches.map((match) => {
            const isLive = match.status === "Đang diễn ra";
            const isPending = match.status === "Chưa đá"; // Chỉ khi chưa đá mới được sửa/xóa

            return (
              <Grid item xs={12} sm={6} md={4} key={match.match_id}>
                <Card
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    boxShadow: 3,
                    position: "relative",
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    {/* Header: Status & Badge */}
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 2,
                      }}
                    >
                      {renderMatchStatus(match)}
                      {match.prediction_id && (
                        <Chip label="Đã dự đoán" color="success" size="small" />
                      )}
                    </Box>

                    {/* Tên sân */}
                    <Box sx={{ textAlign: "center", mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        <LocationOnIcon sx={{ fontSize: 14, mr: 0.5 }} />
                        {match.stadium_name || "Sân vận động"}
                      </Typography>
                    </Box>

                    {/* Logo & LIVE/VS */}
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
                        <img
                          src={
                            match.home_team_logo ||
                            "https://via.placeholder.com/60"
                          }
                          alt="Home"
                          style={{
                            width: 60,
                            height: 60,
                            objectFit: "contain",
                          }}
                        />
                        <Typography
                          variant="subtitle2"
                          sx={{ mt: 1, fontWeight: "bold" }}
                        >
                          {match.home_team_name}
                        </Typography>
                      </Box>

                      {/* Ở GIỮA: LIVE (nhấp nháy) hoặc VS */}
                      <Box sx={{ mx: 1, textAlign: "center" }}>
                        {isLive ? (
                          <Typography
                            variant="h4"
                            color="error"
                            fontWeight="900"
                            sx={{
                              animation: "blink 1s linear infinite",
                              "@keyframes blink": {
                                "0%": { opacity: 1 },
                                "50%": { opacity: 0.2 },
                                "100%": { opacity: 1 },
                              },
                            }}
                          >
                            LIVE
                          </Typography>
                        ) : (
                          <>
                            <Typography
                              variant="h5"
                              sx={{
                                fontWeight: "bold",
                                color: "text.secondary",
                              }}
                            >
                              VS
                            </Typography>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {match.match_datetime
                                ? format(
                                    new Date(match.match_datetime),
                                    "HH:mm"
                                  )
                                : ""}
                            </Typography>
                          </>
                        )}
                      </Box>

                      {/* Đội khách */}
                      <Box sx={{ textAlign: "center", flex: 1 }}>
                        <img
                          src={
                            match.away_team_logo ||
                            "https://via.placeholder.com/60"
                          }
                          alt="Away"
                          style={{
                            width: 60,
                            height: 60,
                            objectFit: "contain",
                          }}
                        />
                        <Typography
                          variant="subtitle2"
                          sx={{ mt: 1, fontWeight: "bold" }}
                        >
                          {match.away_team_name}
                        </Typography>
                      </Box>
                    </Box>

                    {/* KHUNG HIỂN THỊ DỰ ĐOÁN (Luôn hiện nếu có prediction_id) */}
                    {match.prediction_id && (
                      <Box
                        sx={{
                          mt: 2,
                          p: 1.5,
                          bgcolor: "#e8f5e9",
                          borderRadius: 1,
                          border: "1px solid #2e7d32",
                        }}
                      >
                        <Typography
                          variant="caption"
                          sx={{
                            fontWeight: "bold",
                            color: "#1b5e20",
                            display: "flex",
                            justifyContent: "space-between",
                          }}
                        >
                          <span>⚽ Dự đoán của bạn:</span>
                          {/* Nếu trận đã bắt đầu, hiện chữ Đã chốt */}
                          {!isPending && (
                            <span
                              style={{
                                fontSize: "10px",
                                color: "#d32f2f",
                                fontWeight: "bold",
                              }}
                            >
                              (Đã chốt)
                            </span>
                          )}
                        </Typography>

                        <Typography
                          variant="body2"
                          color="#1b5e20"
                          fontWeight="bold"
                          sx={{ mt: 0.5 }}
                        >
                          {match.predicted_card_over_under ? (
                            <span>
                              <FlagIcon
                                sx={{
                                  fontSize: 16,
                                  verticalAlign: "text-bottom",
                                  mr: 0.5,
                                }}
                              />{" "}
                              Thẻ phạt:{" "}
                              {match.predicted_card_over_under === "OVER_3.5"
                                ? "Tài (>3.5)"
                                : "Xỉu (<3.5)"}
                            </span>
                          ) : match.predicted_home_score !== null ? (
                            <span>
                              Tỉ số: {match.predicted_home_score} -{" "}
                              {match.predicted_away_score}
                            </span>
                          ) : (
                            <span>
                              Kết quả:{" "}
                              {match.predicted_result === "HOME_WIN"
                                ? `${match.home_team_name} Thắng`
                                : match.predicted_result === "AWAY_WIN"
                                ? `${match.away_team_name} Thắng`
                                : "Hòa"}
                            </span>
                          )}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>

                  {/* BUTTONS ACTIONS */}
                  <CardActions sx={{ p: 2, pt: 0 }}>
                    {match.prediction_id ? (
                      // Nếu ĐÃ dự đoán
                      isPending ? (
                        // Nếu chưa đá -> Cho phép Sửa/Xóa
                        <Box sx={{ display: "flex", gap: 1, width: "100%" }}>
                          <Button
                            variant="outlined"
                            color="secondary"
                            size="small"
                            fullWidth
                            onClick={() => handleOpenPredictionDialog(match)}
                            startIcon={<EditIcon />}
                          >
                            Sửa
                          </Button>
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            fullWidth
                            onClick={() => handleDeleteClick(match)}
                            startIcon={<DeleteIcon />}
                          >
                            Xóa
                          </Button>
                        </Box>
                      ) : (
                        // Nếu đang đá/xong -> Khóa nút
                        <Button
                          fullWidth
                          variant="contained"
                          disabled
                          startIcon={<LockIcon />}
                        >
                          Đã chốt dự đoán
                        </Button>
                      )
                    ) : (
                      // Nếu CHƯA dự đoán
                      <Button
                        fullWidth
                        variant="contained"
                        onClick={() => handleOpenPredictionDialog(match)}
                        startIcon={<EmojiEventsIcon />}
                        disabled={!isPending} // Không cho dự đoán nếu trận đã live
                      >
                        {isPending ? "Dự đoán ngay" : "Đã đóng dự đoán"}
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* DIALOG FORM */}
      <Dialog
        open={predictionDialogOpen}
        onClose={handleClosePredictionDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Dự đoán trận đấu</DialogTitle>
        <DialogContent>
          {selectedMatch && (
            <>
              <Box sx={{ textAlign: "center", mb: 3 }}>
                <Typography variant="h6">
                  {selectedMatch.home_team_name} vs{" "}
                  {selectedMatch.away_team_name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Chọn loại dự đoán:
                </Typography>
              </Box>

              <FormControl component="fieldset" sx={{ mb: 3, width: "100%" }}>
                <RadioGroup
                  row
                  value={predictionType}
                  onChange={handlePredictionTypeChange}
                  sx={{ justifyContent: "center" }}
                >
                  <FormControlLabel
                    value="result"
                    control={<Radio />}
                    label="Kết quả"
                  />
                  <FormControlLabel
                    value="score"
                    control={<Radio />}
                    label="Tỉ số"
                  />
                  <FormControlLabel
                    value="cards"
                    control={<Radio />}
                    label="Thẻ phạt"
                  />
                </RadioGroup>
              </FormControl>

              <Box sx={{ p: 2, bgcolor: "grey.50", borderRadius: 2 }}>
                {predictionType === "result" && (
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
                )}
                {predictionType === "score" && (
                  <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                    <TextField
                      label={selectedMatch.home_team_name}
                      type="number"
                      value={predictionData.predicted_home_score}
                      onChange={handleScoreChange("predicted_home_score")}
                      fullWidth
                      inputProps={{ min: 0 }}
                    />
                    <Typography variant="h5">-</Typography>
                    <TextField
                      label={selectedMatch.away_team_name}
                      type="number"
                      value={predictionData.predicted_away_score}
                      onChange={handleScoreChange("predicted_away_score")}
                      fullWidth
                      inputProps={{ min: 0 }}
                    />
                  </Box>
                )}
                {predictionType === "cards" && (
                  <FormControl component="fieldset">
                    <Typography variant="subtitle2" gutterBottom>
                      Tổng thẻ phạt (Vàng + Đỏ):
                    </Typography>
                    <RadioGroup
                      value={predictionData.predicted_card_over_under}
                      onChange={handleCardChange}
                    >
                      <FormControlLabel
                        value="OVER_3.5"
                        control={<Radio />}
                        label={
                          <Box>
                            <Typography fontWeight="bold">Tài 3.5</Typography>
                            <Typography variant="caption">
                              Trên 3 thẻ (4, 5...)
                            </Typography>
                          </Box>
                        }
                        sx={{ mb: 1 }}
                      />
                      <FormControlLabel
                        value="UNDER_3.5"
                        control={<Radio />}
                        label={
                          <Box>
                            <Typography fontWeight="bold">Xỉu 3.5</Typography>
                            <Typography variant="caption">
                              Dưới 4 thẻ (0-3)
                            </Typography>
                          </Box>
                        }
                      />
                    </RadioGroup>
                  </FormControl>
                )}
              </Box>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePredictionDialog}>Hủy</Button>
          <Button
            variant="contained"
            onClick={handlePredictionSubmit}
            disabled={submitting}
          >
            {submitting ? "Đang gửi..." : "Xác nhận"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* CONFIRM DELETE */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
      >
        <DialogTitle>Xóa dự đoán?</DialogTitle>
        <DialogContent>
          Bạn có chắc muốn xóa dự đoán cho trận này không?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Hủy</Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
          >
            Xóa
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Container>
  );
};

export default Predictions;
