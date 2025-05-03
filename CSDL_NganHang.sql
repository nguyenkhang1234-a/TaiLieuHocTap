CREATE DATABASE BankingDB;
USE BankingDB;

-- Bảng ChiNhanh
CREATE TABLE ChiNhanh (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    MaCN INT UNIQUE NOT NULL,
    TenCN NVARCHAR(100),
    DiaChi NVARCHAR(200)
);

-- Bảng TaiKhoan
CREATE TABLE TaiKhoan (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    MaTK INT UNIQUE NOT NULL,
    TenTK NVARCHAR(100),
    LoaiTK NVARCHAR(50),
    SoDu DECIMAL(18, 2)
);

-- Bảng GiaoDich
CREATE TABLE GiaoDich (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    MaGD INT UNIQUE NOT NULL,
    MaTK INT,
    MaCN INT,
    LoaiGD INT CHECK (LoaiGD IN (1, 2, 3)), -- 1: Nạp, 2: Rút, 3: Chuyển
    SoTien DECIMAL(18, 2),
    NgayGD DATE,
    FOREIGN KEY (MaTK) REFERENCES TaiKhoan(MaTK),
    FOREIGN KEY (MaCN) REFERENCES ChiNhanh(MaCN)
);

-- Bảng PhatSinh
CREATE TABLE PhatSinh (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    MaPhat INT UNIQUE NOT NULL,
    MaGD INT,
    SoTienPhat DECIMAL(18, 2),
    DaThanhToan BIT,
    FOREIGN KEY (MaGD) REFERENCES GiaoDich(MaGD)
);

-- Dữ liệu ChiNhanh
INSERT INTO ChiNhanh (MaCN, TenCN, DiaChi) VALUES 
(1, N'Chi Nhánh Hà Nội', N'123 Trần Phú, Hà Nội'),
(2, N'Chi Nhánh TP.HCM', N'456 Lê Lợi, TP.HCM'),
(3, N'Chi Nhánh Đà Nẵng', N'789 Nguyễn Văn Linh, Đà Nẵng'),
(4, N'Chi Nhánh Cần Thơ', N'12 Hòa Bình, Cần Thơ'),
(5, N'Chi Nhánh Hải Phòng', N'34 Tôn Đức Thắng, Hải Phòng');

-- Dữ liệu TaiKhoan
INSERT INTO TaiKhoan (MaTK, TenTK, LoaiTK, SoDu) VALUES
(101, N'Nguyễn Văn A', N'Tiết kiệm', 10000000),
(102, N'Trần Thị B', N'Thanh toán', 7500000),
(103, N'Lê Văn C', N'Tiết kiệm', 12000000),
(104, N'Phạm Thị D', N'Thanh toán', 5500000),
(105, N'Đỗ Văn E', N'Tiết kiệm', 8500000);
INSERT INTO TaiKhoan (MaTK, TenTK, LoaiTK, SoDu) VALUES
(106, N'Mai Phương Thảo', N'Tiết kiệm', 100000000);

-- Dữ liệu GiaoDich
INSERT INTO GiaoDich (MaGD, MaTK, MaCN, LoaiGD, SoTien, NgayGD) VALUES
(201, 101, 1, 1, 3000000, '2025-04-01'), -- Nạp
(202, 102, 2, 2, 1000000, '2025-04-03'), -- Rút
(203, 103, 3, 3, 2000000, '2025-04-05'), -- Chuyển
(204, 104, 4, 1, 2500000, '2025-04-07'), -- Nạp
(205, 105, 5, 2, 1500000, '2025-04-10'); -- Rút
INSERT INTO GiaoDich (MaGD, MaTK, MaCN, LoaiGD, SoTien, NgayGD) VALUES
(206, 106, 5, 1, 3000000, '2025-11-09');
INSERT INTO GiaoDich (MaGD, MaTK, MaCN, LoaiGD, SoTien, NgayGD) VALUES
(207, 106, 5, 2, 10000, '2025-11-09');
INSERT INTO GiaoDich (MaGD, MaTK, MaCN, LoaiGD, SoTien, NgayGD) VALUES
(208, 106, 1, 2, 10000, '2025-11-09');

-- Dữ liệu PhatSinh
INSERT INTO PhatSinh (MaPhat, MaGD, SoTienPhat, DaThanhToan) VALUES
(301, 201, 15000, 1),
(302, 202, 10000, 1),
(303, 203, 20000, 0),
(304, 204, 12000, 1),
(305, 205, 18000, 0),
(401, 201, 15000, 1),
(402, 201, 15000, 1);
INSERT INTO PhatSinh (MaPhat, MaGD, SoTienPhat, DaThanhToan) VALUES
(306, 206, 15000, 1);

-- Kiểm tra dữ liệu
SELECT * FROM ChiNhanh;
SELECT * FROM TaiKhoan;
SELECT * FROM GiaoDich;
SELECT * FROM PhatSinh;