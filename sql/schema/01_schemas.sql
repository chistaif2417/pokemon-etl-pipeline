-- Tạo 3 tầng của kiến trúc dữ liệu.
CREATE SCHEMA IF NOT EXISTS raw; -- JSON gốc lấy từ API
CREATE SCHEMA IF NOT EXISTS core; -- Dữ liệu đã chuẩn hóa 3NF
CREATE SCHEMA IF NOT EXISTS analytic; -- View phục vụ phân tích