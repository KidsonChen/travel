CREATE TABLE expenses 
(  
  id INTEGER PRIMARY KEY AUTOINCREMENT,  
  name TEXT NOT NULL,  
  amount REAL NOT NULL,  
  payer TEXT NOT NULL,  
  note TEXT,  
  shared TEXT NOT NULL,  
  date TEXT NOT NULL,  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP  
);  
  
CREATE INDEX idx_payer ON expenses(payer);  
CREATE INDEX idx_date ON expenses(date);  
CREATE INDEX idx_created_at ON expenses(created_at); 
