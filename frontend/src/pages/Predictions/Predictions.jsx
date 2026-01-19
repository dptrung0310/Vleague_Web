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
import LockIcon from "@mui/icons-material/Lock";
import FlagIcon from "@mui/icons-material/Flag";
import SmartDisplayIcon from "@mui/icons-material/SmartDisplay";
import { format } from "date-fns";
import predictionService from "../../services/predictionService";
import "./Predictions.css";
import io from "socket.io-client";

const socket = io("http://localhost:5000");

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

  // --- AI States ---
  const [aiCount, setAiCount] = useState(0);
  const [aiDialogOpen, setAiDialogOpen] = useState(false);
  const [streamUrl, setStreamUrl] = useState("");
  const [aiMatchId, setAiMatchId] = useState(null);

  // --- Result Dialog State ---
  const [resultDialog, setResultDialog] = useState({
    open: false,
    status: "",
    msg: "",
  });

  // Lấy User ID giả lập (Demo: ID = 1)
  const getCurrentUserId = () => {
    try {
      const userStr = localStorage.getItem("user"); // Hoặc "account", "profile" tùy code login của bạn
      if (userStr) {
        const user = JSON.parse(userStr);
        // Kiểm tra xem trường id tên là user_id hay id
        return user.user_id || user.id;
      }
    } catch (e) {
      console.error("Không lấy được User ID:", e);
    }
    return null; // Trả về null nếu chưa đăng nhập
  };

  useEffect(() => {
    // 1. Nhận cập nhật thẻ
    socket.on("ui_update_card_count", (data) => {
      console.log("🔥 AI Update:", data);
      if (data.total_cards !== undefined) setAiCount(data.total_cards);
      else setAiCount((prev) => prev + 1);
    });

    // 2. Nhận kết quả thắng/thua
    socket.on("prediction_result", (data) => {
      console.log("🏁 Kết quả:", data);
      const myId = getCurrentUserId();
      if (String(data.user_id) === String(myId)) {
        const isWin = data.result === "WIN";
        setResultDialog({
          open: true,
          status: data.result,
          msg: isWin
            ? `🎉 CHÚC MỪNG! Bạn đã thắng kèo thẻ phạt! (AI đếm được: ${data.total_cards} thẻ)`
            : `😢 RẤT TIẾC! Bạn đã thua kèo này. (AI đếm được: ${data.total_cards} thẻ)`,
        });
        setAiDialogOpen(false);
      }
    });

    return () => {
      socket.off("ui_update_card_count");
      socket.off("prediction_result");
    };
  }, []);

  const fetchUpcomingMatches = async () => {
    try {
      setLoading(true);
      const response = await predictionService.getUpcomingMatches();
      let matchesData =
        response.data?.matches || response.data?.data?.matches || [];
      if (matchesData.length > 0) {
        matchesData.sort((a, b) => {
          if (a.status === "Đang diễn ra" && b.status !== "Đang diễn ra")
            return -1;
          if (a.status !== "Đang diễn ra" && b.status === "Đang diễn ra")
            return 1;
          return (
            new Date(a.match_datetime || 0) - new Date(b.match_datetime || 0)
          );
        });
        setMatches(matchesData);
      } else setMatches([]);
    } catch (err) {
      setError("Không thể tải danh sách.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUpcomingMatches();
  }, []);

  // --- Handlers AI ---
  const handleOpenAiCheck = (match) => {
    setAiMatchId(match.match_id);
    setAiCount(0);
    setStreamUrl("");
    setAiDialogOpen(true);
  };

  const handleStartAi = async () => {
    if (!streamUrl) return;
    try {
      // Gọi API start kèm user_id
      const response = await fetch("http://localhost:5000/api/ai/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          match_id: aiMatchId,
          stream_url: streamUrl,
          user_id: getCurrentUserId(), // Gửi ID đi
        }),
      });
      if (response.ok)
        setSnackbar({
          open: true,
          message: "AI đang chạy...",
          severity: "info",
        });
      else alert("Lỗi khởi động AI");
    } catch (e) {
      console.error(e);
    }
  };

  // --- Handlers Prediction ---
  const handleOpenPredictionDialog = async (match) => {
    if (match.status !== "Chưa đá")
      return setSnackbar({
        open: true,
        message: "Đã bắt đầu!",
        severity: "warning",
      });
    try {
      const res = await predictionService.checkUserPrediction(match.match_id);
      const pred = res.data?.prediction || res?.prediction;
      if (pred) {
        let type = "result";
        if (pred.predicted_card_over_under) type = "cards";
        else if (pred.predicted_home_score !== null) type = "score";
        setPredictionType(type);
        setPredictionData({
          predicted_result: pred.predicted_result || "HOME_WIN",
          predicted_home_score: pred.predicted_home_score || 0,
          predicted_away_score: pred.predicted_away_score || 0,
          predicted_card_over_under:
            pred.predicted_card_over_under || "OVER_3.5",
        });
      } else {
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
    } catch (e) {}
  };

  const handlePredictionSubmit = async () => {
    if (!selectedMatch) return;
    setSubmitting(true);
    const data = {
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
      if (selectedMatch.prediction_id)
        await predictionService.updatePrediction(
          selectedMatch.prediction_id,
          data
        );
      else await predictionService.createPrediction(data);

      // Reload list logic simplified
      fetchUpcomingMatches();
      setSnackbar({ open: true, message: "Thành công!", severity: "success" });
      setPredictionDialogOpen(false);
    } catch (e) {
      setSnackbar({ open: true, message: "Lỗi", severity: "error" });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteConfirm = async () => {
    try {
      await predictionService.deletePrediction(matchToDelete.prediction_id);
      fetchUpcomingMatches();
      setSnackbar({ open: true, message: "Đã xóa", severity: "success" });
    } catch (e) {}
    setDeleteConfirmOpen(false);
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
        <EmojiEventsIcon sx={{ mr: 1, verticalAlign: "bottom" }} /> Dự Đoán Trận
        Đấu
      </Typography>

      <Grid container spacing={3}>
        {matches.map((match) => {
          const isLive = match.status === "Đang diễn ra";
          const isPending = match.status === "Chưa đá";
          return (
            <Grid item xs={12} sm={6} md={4} key={match.match_id}>
              <Card
                sx={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  boxShadow: 3,
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
                    {isLive ? (
                      <Chip
                        label="LIVE"
                        color="error"
                        size="small"
                        sx={{ animation: "pulse 1.5s infinite" }}
                      />
                    ) : (
                      <Chip
                        icon={<EventIcon />}
                        label={
                          match.match_datetime
                            ? format(
                                new Date(match.match_datetime),
                                "dd/MM HH:mm"
                              )
                            : "N/A"
                        }
                        size="small"
                        variant="outlined"
                      />
                    )}
                    {match.prediction_id && (
                      <Chip label="Đã dự đoán" color="success" size="small" />
                    )}
                  </Box>

                  <Box sx={{ textAlign: "center", mb: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      <LocationOnIcon sx={{ fontSize: 14 }} />{" "}
                      {match.stadium_name}
                    </Typography>
                  </Box>

                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <Box sx={{ textAlign: "center", flex: 1 }}>
                      <img
                        src={
                          match.home_team_logo ||
                          "https://via.placeholder.com/60"
                        }
                        alt="Home"
                        style={{ width: 60, height: 60, objectFit: "contain" }}
                      />
                      <Typography variant="subtitle2" fontWeight="bold">
                        {match.home_team_name}
                      </Typography>
                    </Box>
                    <Box sx={{ mx: 1, textAlign: "center" }}>
                      {isLive ? (
                        <Box
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                          }}
                        >
                          <Typography
                            variant="h4"
                            color="error"
                            fontWeight="900"
                            sx={{ animation: "blink 1s infinite" }}
                          >
                            LIVE
                          </Typography>
                          <Box sx={{ mt: 1, display: "flex", gap: 0.5 }}>
                            <Chip
                              icon={<SmartDisplayIcon />}
                              label={`Số thẻ: ${aiCount}`}
                              color="warning"
                              size="small"
                            />
                            <Button
                              variant="contained"
                              color="warning"
                              size="small"
                              sx={{
                                fontSize: "0.65rem",
                                minWidth: "auto",
                                px: 1,
                              }}
                              onClick={() => handleOpenAiCheck(match)}
                            >
                              AI
                            </Button>
                          </Box>
                        </Box>
                      ) : (
                        <>
                          <Typography
                            variant="h5"
                            fontWeight="bold"
                            color="text.secondary"
                          >
                            VS
                          </Typography>
                          <Typography variant="caption">
                            {match.match_datetime
                              ? format(new Date(match.match_datetime), "HH:mm")
                              : ""}
                          </Typography>
                        </>
                      )}
                    </Box>
                    <Box sx={{ textAlign: "center", flex: 1 }}>
                      <img
                        src={
                          match.away_team_logo ||
                          "https://via.placeholder.com/60"
                        }
                        alt="Away"
                        style={{ width: 60, height: 60, objectFit: "contain" }}
                      />
                      <Typography variant="subtitle2" fontWeight="bold">
                        {match.away_team_name}
                      </Typography>
                    </Box>
                  </Box>

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
                        <span>⚽ Dự đoán của bạn:</span>{" "}
                        {!isPending && (
                          <span style={{ fontSize: "10px", color: "#d32f2f" }}>
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
                              }}
                            />{" "}
                            Thẻ: {match.predicted_card_over_under}
                          </span>
                        ) : match.predicted_home_score !== null ? (
                          <span>
                            Tỉ số: {match.predicted_home_score} -{" "}
                            {match.predicted_away_score}
                          </span>
                        ) : (
                          <span>Kết quả: {match.predicted_result}</span>
                        )}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
                <CardActions sx={{ p: 2, pt: 0 }}>
                  {match.prediction_id ? (
                    isPending ? (
                      <Box sx={{ display: "flex", gap: 1, width: "100%" }}>
                        <Button
                          variant="outlined"
                          color="secondary"
                          fullWidth
                          onClick={() => handleOpenPredictionDialog(match)}
                          startIcon={<EditIcon />}
                        >
                          Sửa
                        </Button>
                        <Button
                          variant="outlined"
                          color="error"
                          fullWidth
                          onClick={() => {
                            setMatchToDelete(match);
                            setDeleteConfirmOpen(true);
                          }}
                          startIcon={<DeleteIcon />}
                        >
                          Xóa
                        </Button>
                      </Box>
                    ) : (
                      <Button
                        fullWidth
                        variant="contained"
                        disabled
                        startIcon={<LockIcon />}
                      >
                        Đã chốt
                      </Button>
                    )
                  ) : (
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={() => handleOpenPredictionDialog(match)}
                      disabled={!isPending}
                    >
                      {isPending ? "Dự đoán ngay" : "Đã đóng"}
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* DIALOGS */}
      <Dialog
        open={predictionDialogOpen}
        onClose={() => setPredictionDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Dự đoán</DialogTitle>
        <DialogContent>
          <FormControl component="fieldset" sx={{ width: "100%", mt: 1 }}>
            <RadioGroup
              row
              value={predictionType}
              onChange={(e) => setPredictionType(e.target.value)}
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
                onChange={(e) =>
                  setPredictionData({
                    ...predictionData,
                    predicted_result: e.target.value,
                  })
                }
              >
                <FormControlLabel
                  value="HOME_WIN"
                  control={<Radio />}
                  label="Chủ nhà thắng"
                />
                <FormControlLabel
                  value="DRAW"
                  control={<Radio />}
                  label="Hòa"
                />
                <FormControlLabel
                  value="AWAY_WIN"
                  control={<Radio />}
                  label="Khách thắng"
                />
              </RadioGroup>
            )}
            {predictionType === "score" && (
              <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
                <TextField
                  type="number"
                  label="Chủ"
                  value={predictionData.predicted_home_score}
                  onChange={(e) =>
                    setPredictionData({
                      ...predictionData,
                      predicted_home_score: parseInt(e.target.value) || 0,
                    })
                  }
                  fullWidth
                />
                <Typography>-</Typography>
                <TextField
                  type="number"
                  label="Khách"
                  value={predictionData.predicted_away_score}
                  onChange={(e) =>
                    setPredictionData({
                      ...predictionData,
                      predicted_away_score: parseInt(e.target.value) || 0,
                    })
                  }
                  fullWidth
                />
              </Box>
            )}
            {predictionType === "cards" && (
              <RadioGroup
                value={predictionData.predicted_card_over_under}
                onChange={(e) =>
                  setPredictionData({
                    ...predictionData,
                    predicted_card_over_under: e.target.value,
                  })
                }
              >
                <FormControlLabel
                  value="OVER_3.5"
                  control={<Radio />}
                  label="Tài 3.5 (>3 thẻ)"
                />
                <FormControlLabel
                  value="UNDER_3.5"
                  control={<Radio />}
                  label="Xỉu 3.5 (<=3 thẻ)"
                />
              </RadioGroup>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPredictionDialogOpen(false)}>Hủy</Button>
          <Button
            variant="contained"
            onClick={handlePredictionSubmit}
            disabled={submitting}
          >
            Lưu
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={aiDialogOpen}
        onClose={() => setAiDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <SmartDisplayIcon color="warning" /> AI VAR Check
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2, mt: 1 }}>
            Nhập link video (.mp4/.m3u8):
          </Typography>
          <TextField
            fullWidth
            label="URL"
            value={streamUrl}
            onChange={(e) => setStreamUrl(e.target.value)}
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAiDialogOpen(false)}>Hủy</Button>
          <Button variant="contained" color="warning" onClick={handleStartAi}>
            Chạy AI
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
      >
        <DialogTitle>Xác nhận xóa?</DialogTitle>
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

      <Dialog
        open={resultDialog.open}
        onClose={() => setResultDialog({ ...resultDialog, open: false })}
      >
        <DialogTitle
          sx={{
            color: resultDialog.status === "WIN" ? "green" : "red",
            fontWeight: "bold",
            textAlign: "center",
          }}
        >
          {resultDialog.status === "WIN" ? "CHIẾN THẮNG! 🏆" : "THẤT BẠI 💔"}
        </DialogTitle>
        <DialogContent>
          <Typography variant="h6" align="center">
            {resultDialog.msg}
          </Typography>
        </DialogContent>
        <DialogActions sx={{ justifyContent: "center" }}>
          <Button
            variant="contained"
            onClick={() => setResultDialog({ ...resultDialog, open: false })}
          >
            Đóng
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
