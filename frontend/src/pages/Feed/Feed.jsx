// src/pages/Feed/Feed.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import postService from "../../services/postService"; // Import service vừa tạo
import Avatar from "../../components/Avatar"; // Tận dụng lại component Avatar

// --- HELPER: Component hiển thị từng bài Post ---
const PostItem = ({ post, currentUser, onDelete, onLike }) => {
  const [showComment, setShowComment] = useState(false);
  const [commentText, setCommentText] = useState("");
  const [comments, setComments] = useState(post.comments || []);
  const [isLiked, setIsLiked] = useState(post.is_liked);
  const [likeCount, setLikeCount] = useState(post.like_count);

  // Xử lý hiển thị thời gian
  const formatDate = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit",
    });
  };

  // Xử lý Like
  const handleLike = async () => {
    // Optimistic UI: Cập nhật giao diện trước khi gọi API
    const newStatus = !isLiked;
    setIsLiked(newStatus);
    setLikeCount((prev) => (newStatus ? prev + 1 : prev - 1));

    try {
      await postService.toggleLike(post.post_id);
      onLike(); // Refresh lại list cha nếu cần (hoặc không cần cũng được)
    } catch (error) {
      // Revert nếu lỗi
      setIsLiked(!newStatus);
      setLikeCount((prev) => (!newStatus ? prev + 1 : prev - 1));
    }
  };

  // Xử lý gửi Comment
  const handleSendComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    try {
      const res = await postService.addComment(post.post_id, commentText);
      if (res && res.data) {
        setComments([...comments, res.data]); // Thêm comment mới vào list
        setCommentText("");
      }
    } catch (error) {
      console.error("Lỗi comment:", error);
    }
  };

  // Kiểm tra quyền xóa bài
  const isOwner = currentUser && post.user_id === currentUser.user_id;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-4">
      {/* Header: Avatar + Info */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex gap-3">
          <Avatar user={post.user} className="w-10 h-10" />
          <div>
            <h3 className="font-bold text-gray-900 text-sm">
              {post.user?.full_name || post.user?.username}
            </h3>
            <p className="text-xs text-gray-500">
              {formatDate(post.created_at)}
            </p>
          </div>
        </div>
        {isOwner && (
          <button
            onClick={() => onDelete(post.post_id)}
            className="text-gray-400 hover:text-red-500 text-sm"
            title="Xóa bài viết"
          >
            ✕
          </button>
        )}
      </div>

      {/* Content */}
      <div className="mb-3">
        <h4 className="font-semibold text-gray-800 mb-1">{post.title}</h4>
        <p className="text-gray-600 whitespace-pre-line text-sm">
          {post.content}
        </p>
      </div>

      {/* Image */}
      {post.image_url && (
        <div className="mb-3 rounded-lg overflow-hidden border border-gray-100">
          {/* Thêm prefix http://localhost:5000 nếu là ảnh từ backend */}
          <img
            src={
              post.image_url.startsWith("http")
                ? post.image_url
                : `http://localhost:5000${post.image_url}`
            }
            alt="Post content"
            className="w-full object-cover max-h-[500px]"
          />
        </div>
      )}

      {/* Tags (Match/Team/Player) */}
      <div className="flex gap-2 mb-3">
        {post.match && (
          <span className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-full font-medium">
            ⚽ {post.match.name}
          </span>
        )}
        {post.team && (
          <span className="text-xs bg-green-50 text-green-600 px-2 py-1 rounded-full font-medium">
            🛡️ {post.team.name}
          </span>
        )}
        {post.player && (
          <span className="text-xs bg-yellow-50 text-yellow-600 px-2 py-1 rounded-full font-medium">
            🏃 {post.player.name}
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-6 border-t pt-3 text-sm text-gray-500">
        <button
          onClick={handleLike}
          className={`flex items-center gap-2 hover:text-red-500 transition ${
            isLiked ? "text-red-500 font-bold" : ""
          }`}
        >
          {isLiked ? "❤️" : "🤍"} {likeCount} Thích
        </button>
        <button
          onClick={() => setShowComment(!showComment)}
          className="flex items-center gap-2 hover:text-blue-500 transition"
        >
          💬 {comments.length} Bình luận
        </button>
      </div>

      {/* Comment Section */}
      {showComment && (
        <div className="mt-4 pt-4 border-t bg-gray-50 -mx-4 px-4 pb-2">
          {/* List Comment */}
          <div className="space-y-3 mb-4 max-h-60 overflow-y-auto">
            {comments.map((cmt) => (
              <div key={cmt.comment_id} className="flex gap-2">
                <Avatar user={cmt.user} className="w-8 h-8" />
                <div className="bg-white p-2 rounded-lg border text-sm flex-1">
                  <span className="font-bold block text-xs text-gray-700">
                    {cmt.user?.username}
                  </span>
                  <span>{cmt.content}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Form Input */}
          <form onSubmit={handleSendComment} className="flex gap-2">
            <input
              type="text"
              placeholder="Viết bình luận..."
              className="flex-1 px-3 py-2 text-sm border rounded-full focus:outline-none focus:border-blue-500"
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
            />
            <button
              type="submit"
              className="text-blue-600 font-bold text-sm px-2"
            >
              Gửi
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

// --- MAIN COMPONENT ---
const Feed = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);

  // Form State
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    // 1. Lấy user hiện tại
    const userStr = localStorage.getItem("user");
    if (userStr) setCurrentUser(JSON.parse(userStr));

    // 2. Tải bài viết
    loadPosts();
  }, []);

  const loadPosts = async (query = "") => {
    setLoading(true);
    try {
      // Sửa: Dùng postService thay vì axios trực tiếp (tránh lỗi axios is not defined)
      // Lưu ý: Đảm bảo bạn đã sửa file postService.js để nhận tham số 'search' như hướng dẫn trước
      const res = await postService.getPosts(1, 10, query);

      // Sửa: Kiểm tra kỹ 2 trường hợp cấu trúc dữ liệu để không bị mất bài
      if (res) {
        // Trường hợp 1: API trả về chuẩn { status: "success", data: { posts: [...] } }
        // Và axiosClient trả về res.data
        if (res.data && res.data.posts) {
          setPosts(res.data.posts);
        }
        // Trường hợp 2: Nếu axiosClient chưa xử lý, dữ liệu lồng sâu hơn (res.data.data.posts)
        else if (res.data && res.data.data && res.data.data.posts) {
          setPosts(res.data.data.posts);
        }
        // Trường hợp 3: Fallback (nếu API trả thẳng mảng posts)
        else if (Array.isArray(res.data)) {
          setPosts(res.data);
        }
      }
    } catch (error) {
      console.error("Lỗi tải feed:", error);
    } finally {
      setLoading(false);
    }
  };

  // Xử lý khi nhấn nút Tìm kiếm
  const handleSearch = (e) => {
    e.preventDefault();
    loadPosts(searchTerm);
  };

  // Xử lý khi xóa trắng ô tìm kiếm thì load lại tất cả
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    if (e.target.value === "") {
      loadPosts("");
    }
  };

  // Xử lý chọn ảnh
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  // Xử lý đăng bài
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim() && !image) return alert("Hãy viết gì đó!");

    setIsSubmitting(true);
    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);
    if (image) formData.append("image", image);
    // Nếu muốn test tag, bạn có thể hardcode hoặc thêm input vào form:
    // formData.append("match_id", "1");

    try {
      const res = await postService.createPost(formData);
      if (res && res.data) {
        // Thêm bài mới vào đầu danh sách
        setPosts([res.data, ...posts]);
        // Reset form
        setTitle("");
        setContent("");
        setImage(null);
        setPreview(null);
      }
    } catch (error) {
      alert(error.response?.data?.message || "Đăng bài thất bại");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Xử lý xóa bài
  const handleDeletePost = async (postId) => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa bài này?")) return;
    try {
      await postService.deletePost(postId);
      // Xóa khỏi danh sách UI
      setPosts(posts.filter((p) => p.post_id !== postId));
    } catch (error) {
      alert("Lỗi khi xóa bài");
    }
  };

  return (
    <div className="bg-gray-100 min-h-screen py-6">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* === THANH TÌM KIẾM === */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              placeholder="Tìm kiếm bài viết, người dùng..."
              // Thay đổi className để có màu xanh nhạt, chữ xanh đậm
              className="flex-1 bg-blue-50 border border-blue-200 text-blue-800 placeholder-blue-400 rounded-lg px-4 py-2 text-sm focus:outline-none focus:bg-white focus:border-blue-600 transition-colors shadow-sm"
              value={searchTerm}
              onChange={handleSearchChange}
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 transition"
            >
              Tìm
            </button>
          </form>
        </div>
        {/* === CREATE POST CARD === */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex gap-3 mb-4">
            {currentUser && <Avatar user={currentUser} className="w-10 h-10" />}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Tiêu đề..."
                // Thay đổi className: Nền xanh nhạt, bo góc, chữ đậm màu xanh
                className="w-full text-sm font-bold text-blue-900 placeholder-blue-300 mb-3 px-3 py-2 bg-blue-50 border border-blue-100 rounded-lg focus:outline-none focus:bg-white focus:border-blue-500 transition-colors"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <textarea
                placeholder={`Bạn đang nghĩ gì, ${
                  currentUser?.username || "bạn ơi"
                }?`}
                className="w-full bg-gray-50 rounded-lg p-3 text-sm focus:outline-none focus:ring-1 ring-blue-200 resize-none h-24"
                value={content}
                onChange={(e) => setContent(e.target.value)}
              ></textarea>
            </div>
          </div>

          {/* Image Preview */}
          {preview && (
            <div className="relative mb-4">
              <img
                src={preview}
                alt="Preview"
                className="w-full rounded-lg max-h-60 object-cover"
              />
              <button
                onClick={() => {
                  setImage(null);
                  setPreview(null);
                }}
                className="absolute top-2 right-2 bg-gray-900 bg-opacity-70 text-white rounded-full p-1 text-xs hover:bg-red-500"
              >
                ✕
              </button>
            </div>
          )}

          <div className="flex justify-between items-center pt-2 border-t">
            <label className="flex items-center gap-2 text-gray-500 text-sm cursor-pointer hover:bg-gray-50 px-3 py-2 rounded transition">
              <span>📷 Tải lên ảnh</span>
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleImageChange}
              />
            </label>

            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className={`bg-blue-600 text-white px-6 py-2 rounded-lg font-bold text-sm shadow-md hover:bg-blue-700 transition ${
                isSubmitting ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {isSubmitting ? "Đang đăng..." : "Đăng bài"}
            </button>
          </div>
        </div>

        {/* === POST LIST === */}
        {loading ? (
          <div className="text-center py-10 text-gray-500">
            Đang tải bảng tin...
          </div>
        ) : (
          <div>
            {posts.map((post) => (
              <PostItem
                key={post.post_id}
                post={post}
                currentUser={currentUser}
                onDelete={handleDeletePost}
                onLike={() => {}} // Có thể gọi reload nếu muốn đồng bộ hoàn hảo
              />
            ))}

            {posts.length === 0 && (
              <div className="text-center py-10 text-gray-500 bg-white rounded-xl">
                Chưa có bài viết nào. Hãy là người đầu tiên!
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Feed;
