-- Lưu dữ liệu thô và nhật kí chạy

-- Lưu nguyên JSON phản hồi từ API
CREATE TABLE raw.RAW_API_RESPONSE (
	endpoint TEXT NOT NULL, -- Ví dụ 'pokemon', 'pokemon-species'
	resource_id INT NOT NULL, -- id của tài nguyên
	payload JSONB NOT NULL, -- JSON gốc
	fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(), 
	PRIMARY KEY (endpoint, resource_id)
);

-- Nhật ký mỗi lần chạy pipeline
CREATE TABLE core.etl_run_log (
	run_id SERIAL PRIMARY KEY,
	started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
	finished_at TIMESTAMPTZ,
	status TEXT NOT NULL DEFAULT 'RUNNING', -- RUNNING/SUCCESS/FAILED
	rows_read INT,
	rows_written INT,
	rows_rejected INT,
	message TEXT
);