CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT,

    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending', 'In Progress', 'Resolved')),

    priority TEXT NOT NULL DEFAULT 'Low'
        CHECK (priority IN ('Low', 'Medium', 'High')),

    created_by TEXT NOT NULL,

    support_count INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);


CREATE TABLE IF NOT EXISTS complaint_support (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    complaint_id INTEGER NOT NULL,

    user_id TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (complaint_id)
        REFERENCES complaints(id)
        ON DELETE CASCADE,

    UNIQUE (complaint_id, user_id)
);


-- Indexes for faster filtering/searching.

CREATE INDEX IF NOT EXISTS idx_complaints_category
    ON complaints(category);

CREATE INDEX IF NOT EXISTS idx_complaints_status
    ON complaints(status);

CREATE INDEX IF NOT EXISTS idx_complaints_priority
    ON complaints(priority);

CREATE INDEX IF NOT EXISTS idx_complaints_created_at
    ON complaints(created_at);

CREATE INDEX IF NOT EXISTS idx_complaint_support_complaint_id
    ON complaint_support(complaint_id);