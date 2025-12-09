import React from "react";
const API_URL = "http://localhost:5000"; // URL Backend

const Avatar = ({
  src,
  alt = "Avatar",
  className = "w-10 h-10 rounded-full",
}) => {
  const getAvatarUrl = (url) => {
    if (!url) return "https://via.placeholder.com/150?text=U";
    if (url.startsWith("http")) return url;
    return `${API_URL}${url}`;
  };

  return (
    <img
      src={getAvatarUrl(src)}
      alt={alt}
      className={`object-cover border border-gray-200 bg-gray-100 ${className}`}
      onError={(e) => {
        e.target.src = "https://via.placeholder.com/150?text=Error";
      }}
    />
  );
};
export default Avatar;
