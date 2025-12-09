// src/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'; // <--- Thêm dòng này
import App from './App.jsx'
import './index.css'

// Client ID lấy từ file .env backend bạn gửi
const GOOGLE_CLIENT_ID = "132242481387-g1bljaur91uf5spfh41g4o7lekjh7ldp.apps.googleusercontent.com";

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}> {/* <--- Bọc ngoài cùng */}
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </GoogleOAuthProvider>
  </React.StrictMode>,
)