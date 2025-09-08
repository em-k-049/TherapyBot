-- Initialize database for TherapyBot
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Insert default roles
INSERT INTO roles (name) VALUES ('patient'), ('consultant'), ('admin') ON CONFLICT (name) DO NOTHING;