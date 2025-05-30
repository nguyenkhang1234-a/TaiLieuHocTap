from flask import Flask, render_template, request, jsonify

import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('banking.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('banking.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ChiNhanh (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            MaCN INTEGER UNIQUE NOT NULL,
            TenCN TEXT,
            DiaChi TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TaiKhoan (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            MaTK INTEGER UNIQUE NOT NULL,
            TenTK TEXT,
            LoaiTK TEXT,
            SoDu REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GiaoDich (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            MaGD INTEGER UNIQUE NOT NULL,
            MaTK INTEGER,
            MaCN INTEGER,
            LoaiGD INTEGER CHECK (LoaiGD IN (1, 2, 3)),
            SoTien REAL,
            NgayGD TEXT,
            FOREIGN KEY (MaTK) REFERENCES TaiKhoan(MaTK),
            FOREIGN KEY (MaCN) REFERENCES ChiNhanh(MaCN)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PhatSinh (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            MaPhat INTEGER UNIQUE NOT NULL,
            MaGD INTEGER,
            SoTienPhat REAL,
            DaThanhToan INTEGER,
            FOREIGN KEY (MaGD) REFERENCES GiaoDich(MaGD)
        )
    ''')

    cursor.executemany('''
        INSERT OR IGNORE INTO ChiNhanh (MaCN, TenCN, DiaChi) VALUES (?, ?, ?)
    ''', [
        (1, 'Chi Nhánh Hà Nội', '123 Trần Phú, Hà Nội'),
        (2, 'Chi Nhánh TP.HCM', '456 Lê Lợi, TP.HCM'),
        (3, 'Chi Nhánh Đà Nẵng', '789 Nguyễn Văn Linh, Đà Nẵng'),
        (4, 'Chi Nhánh Cần Thơ', '12 Hòa Bình, Cần Thơ'),
        (5, 'Chi Nhánh Hải Phòng', '34 Tôn Đức Thắng, Hải Phòng')
    ])
    cursor.executemany('''
        INSERT OR IGNORE INTO TaiKhoan (MaTK, TenTK, LoaiTK, SoDu) VALUES (?, ?, ?, ?)
    ''', [
        (101, 'Nguyễn Văn A', 'Tiết kiệm', 10000000),
        (102, 'Trần Thị B', 'Thanh toán', 7500000),
        (103, 'Lê Văn C', 'Tiết kiệm', 12000000),
        (104, 'Phạm Thị D', 'Thanh toán', 5500000),
        (105, 'Đỗ Văn E', 'Tiết kiệm', 8500000),
        (106, 'Mai Phương Thảo', 'Tiết kiệm', 100000000)
    ])
    cursor.executemany('''
        INSERT OR IGNORE INTO GiaoDich (MaGD, MaTK, MaCN, LoaiGD, SoTien, NgayGD) VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        (201, 101, 1, 1, 3000000, '2025-04-01'),
        (202, 102, 2, 2, 1000000, '2025-04-03'),
        (203, 103, 3, 3, 2000000, '2025-04-05'),
        (204, 104, 4, 1, 2500000, '2025-04-07'),
        (205, 105, 5, 2, 1500000, '2025-04-10'),
        (206, 106, 5, 1, 3000000, '2025-11-09'),
        (207, 106, 5, 2, 10000, '2025-11-09'),
        (208, 106, 1, 2, 10000, '2025-11-09')
    ])
    cursor.executemany('''
        INSERT OR IGNORE INTO PhatSinh (MaPhat, MaGD, SoTienPhat, DaThanhToan) VALUES (?, ?, ?, ?)
    ''', [
        (301, 201, 15000, 1),
        (302, 202, 10000, 1),
        (303, 203, 20000, 0),
        (304, 204, 12000, 1),
        (305, 205, 18000, 0),
        (401, 201, 15000, 1),
        (402, 201, 15000, 1),
        (306, 206, 15000, 1)
    ])
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/taikhoan", methods=["GET", "POST"])
def thong_tin_tai_khoan():
    if request.method == 'POST':
        matk = request.form.get("MaTK")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) AS SoLan FROM GiaoDich WHERE MaTK = ?", (matk,))
            so_lan_gd = cursor.fetchone()["SoLan"]

            cursor.execute("SELECT TenTK FROM TaiKhoan WHERE MaTK = ?", (matk,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return render_template("taikhoan.html", thong_tin=None)
            tentk = row["TenTK"]

            cursor.execute("SELECT IFNULL(SUM(SoTien), 0) AS TongNap FROM GiaoDich WHERE MaTK = ? AND LoaiGD = 1", (matk,))
            tong_nap = cursor.fetchone()["TongNap"]

            cursor.execute("SELECT IFNULL(SUM(SoTien), 0) AS TongRut FROM GiaoDich WHERE MaTK = ? AND LoaiGD = 2", (matk,))
            tong_rut = cursor.fetchone()["TongRut"]

            cursor.execute("""
                SELECT DISTINCT c.TenCN FROM GiaoDich g
                JOIN ChiNhanh c ON g.MaCN = c.MaCN
                WHERE g.MaTK = ?
            """, (matk,))
            chi_nhanh = [row["TenCN"] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT IFNULL(SUM(p.SoTienPhat), 0) AS TongPhi
                FROM PhatSinh p
                JOIN GiaoDich g ON p.MaGD = g.MaGD
                WHERE g.MaTK = ?
            """, (matk,))
            tong_phi = cursor.fetchone()["TongPhi"]

            conn.close()

            thong_tin = {
                "MaTK": matk,
                "TenTK": tentk,
                "SoLanGiaoDich": so_lan_gd,
                "TongTienNap": tong_nap,
                "TongTienRut": tong_rut,
                "ChiNhanhGiaoDich": chi_nhanh,
                "TongPhiPhatSinh": tong_phi
            }
            return render_template("taikhoan.html", thong_tin=thong_tin)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return render_template("taikhoan.html", thong_tin=None)
@app.route("/giaodich", methods=["GET", "POST"])
def them_giao_dich():
    if request.method == "POST":
        try:
            data = request.form
            matk = data["MaTK"]
            macn = data["MaCN"]
            loai_gd = int(data["LoaiGD"])
            sotien = float(data["SoTien"])
            ngay = data["NgayGD"]
            magd = data["MaGD"]

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) AS count FROM TaiKhoan WHERE MaTK = ?", (matk,))
            if cursor.fetchone()["count"] == 0:
                conn.close()
                return render_template("giaodich.html", error="Tài khoản không tồn tại.")

            cursor.execute("SELECT COUNT(*) AS count FROM ChiNhanh WHERE MaCN = ?", (macn,))
            if cursor.fetchone()["count"] == 0:
                conn.close()
                return render_template("giaodich.html", error="Chi nhánh không tồn tại.")

            cursor.execute("""
                INSERT INTO GiaoDich (MaGD, MaTK, MaCN, LoaiGD, SoTien, NgayGD)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (magd, matk, macn, loai_gd, sotien, ngay))

            if loai_gd == 1:
                cursor.execute("UPDATE TaiKhoan SET SoDu = SoDu + ? WHERE MaTK = ?", (sotien, matk))
            elif loai_gd in [2, 3]:
                cursor.execute("UPDATE TaiKhoan SET SoDu = SoDu - ? WHERE MaTK = ?", (sotien, matk))

            conn.commit()
            conn.close()
            return render_template("giaodich.html", message="Thêm giao dịch thành công!")

        except Exception as e:
            return render_template("giaodich.html", error=str(e))
        
    return render_template("giaodich.html")

@app.route("/phatsinh", methods=["GET", "POST"])
def danh_sach_phat_sinh():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            maphat = request.form.get("MaPhat")
            cursor.execute("SELECT MaPhat, DaThanhToan FROM PhatSinh WHERE MaPhat = ?", (maphat,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return render_template("phatsinh.html", thong_tin=None, error="Không tìm thấy phát sinh.")

            if row[1] == 0:
                cursor.execute("DELETE FROM PhatSinh WHERE MaPhat = ?", (maphat,))
                conn.commit()
                # Sau khi xóa xong, lấy lại danh sách mới
                cursor.execute("SELECT MaPhat, MaGD, SoTienPhat, DaThanhToan FROM PhatSinh WHERE DaThanhToan = 0")
                data = cursor.fetchall()
                conn.close()
                return render_template("phatsinh.html", records=data, message="Phát sinh đã được xóa thành công!")
            else:
                conn.close()
                return render_template("phatsinh.html", thong_tin=None, error="Không thể xóa: Phát sinh đã thanh toán.")
        else:
            # Với GET thì cũng lấy danh sách phát sinh chưa thanh toán
            cursor.execute("SELECT MaPhat, MaGD, SoTienPhat, DaThanhToan FROM PhatSinh WHERE DaThanhToan = 0")
            data = cursor.fetchall()
            conn.close()
            return render_template("phatsinh.html", records=data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/chinhanh", methods=["GET", "POST"])
def thong_tin_chi_nhanh():
    if request.method == 'POST':
        machinanh = request.form.get("MaCN")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT TenCN FROM ChiNhanh WHERE MaCN = ?", (machinanh,))
            chi_nhanh = cursor.fetchone()
            if not chi_nhanh:
                return render_template("chinhanh.html", thong_tin=None, error="Không tìm thấy chi nhánh.")

            cursor.execute("""
                SELECT g.MaGD, g.MaTK, g.SoTien, g.LoaiGD, g.NgayGD
                FROM GiaoDich g
                WHERE g.MaCN = ?
                ORDER BY g.NgayGD DESC
            """, (machinanh,))
            giao_dich = cursor.fetchall()

            danh_sach_gd = [{"MaGD": gd[0], "MaTK": gd[1], "SoTien": gd[2], "LoaiGD": "Nạp" if gd[3] == 1 else "Rút", "NgayGD": gd[4]} for gd in giao_dich]

            thong_tin = {
                "MaCN": machinanh,
                "TenCN": chi_nhanh[0],
                "DanhSachGiaoDich": danh_sach_gd
            }
            return render_template("chinhanh.html", thong_tin=thong_tin)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return render_template("chinhanh.html")

@app.route("/capnhat", methods=["GET", "POST"])
def cap_nhat_tai_khoan():
    thong_tin, message, error, show_update_form, danh_sach_tk = None, None, None, False, []
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == "POST":
            matk = request.form.get("MaTK")
            action = request.form.get("action")

            if action == "tim":
                cursor.execute("SELECT TenTK, LoaiTK FROM TaiKhoan WHERE MaTK = ?", (matk,))
                row = cursor.fetchone()
                if row:
                    thong_tin = {"MaTK": matk, "TenTK": row[0], "LoaiTK": row[1]}
                    show_update_form = True
                else:
                    error = "Không tìm thấy tài khoản."

            elif action == "capnhat":
                ten_moi = request.form.get("TenTK")
                loai_moi = request.form.get("LoaiTK")
                cursor.execute("""
                    UPDATE TaiKhoan 
                    SET TenTK = ?, LoaiTK = ? 
                    WHERE MaTK = ?
                """, (ten_moi, loai_moi, matk))
                conn.commit()
                message = "Cập nhật tài khoản thành công!"
                thong_tin = {"MaTK": matk, "TenTK": ten_moi, "LoaiTK": loai_moi}
                show_update_form = True

        if show_update_form:
            cursor.execute("SELECT MaTK, TenTK, LoaiTK FROM TaiKhoan ORDER BY MaTK")
            danh_sach_tk = cursor.fetchall()

    except Exception as e:
        error = f"Lỗi: {e}"
    finally:
        if conn:
            conn.close()

    return render_template("capnhat.html",
                           thong_tin=thong_tin,
                           message=message,
                           error=error,
                           show_update_form=show_update_form,
                           danh_sach_tk=danh_sach_tk)

@app.route("/trungbinhcao", methods=["GET"])
def tai_khoan_trung_binh_cao():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                gd.MaTK, 
                tk.TenTK, 
                AVG(gd.SoTien) AS TrungBinhCao
            FROM GiaoDich gd
            JOIN TaiKhoan tk ON gd.MaTK = tk.MaTK
            GROUP BY gd.MaTK, tk.TenTK
            HAVING AVG(gd.SoTien) > 1000000  
            ORDER BY TrungBinhCao DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template("trungbinhcao.html", data=data)
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500
    
@app.route("/them_chinhanh", methods=["GET", "POST"])
def them_chinhanh():
    message = ""
    chi_nhanh = None
    ma_cn = ten_cn = dia_chi = ""

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        ma_cn = request.form["MaCN"].strip()
        ten_cn = request.form.get("TenCN", "").strip()
        dia_chi = request.form.get("DiaChi", "").strip()

        cursor.execute("SELECT * FROM ChiNhanh WHERE MaCN = ?", (ma_cn,))
        existing = cursor.fetchone()

        if existing:
            if ten_cn and dia_chi:
                cursor.execute("UPDATE ChiNhanh SET TenCN = ?, DiaChi = ? WHERE MaCN = ?",
                               (ten_cn, dia_chi, ma_cn))
                conn.commit()
                message = "Cập nhật chi nhánh thành công!"
                cursor.execute("SELECT * FROM ChiNhanh WHERE MaCN = ?", (ma_cn,))
                chi_nhanh = cursor.fetchone()
            else:
                chi_nhanh = existing
                message = "Chi nhánh đã tồn tại. Vui lòng nhập đầy đủ thông tin để cập nhật."
        else:
            if ten_cn and dia_chi:
                try:
                    cursor.execute("INSERT INTO ChiNhanh (MaCN, TenCN, DiaChi) VALUES (?, ?, ?)",
                                   (ma_cn, ten_cn, dia_chi))
                    conn.commit()
                    message = "Thêm chi nhánh thành công!"
                    cursor.execute("SELECT * FROM ChiNhanh WHERE MaCN = ?", (ma_cn,))
                    chi_nhanh = cursor.fetchone()
                except sqlite3.IntegrityError:
                    message = "Lỗi: Mã chi nhánh không hợp lệ hoặc bị trùng."
            else:
                message = "Chi nhánh chưa tồn tại. Vui lòng nhập đầy đủ thông tin để thêm mới."
                chi_nhanh = {"MaCN": ma_cn, "TenCN": ten_cn, "DiaChi": dia_chi}

    # Lấy danh sách chi nhánh để hiển thị cho cả GET và POST
    cursor.execute("SELECT * FROM ChiNhanh")
    ds_chi_nhanh = cursor.fetchall()

    conn.close()
    return render_template("them_chinhanh.html", message=message, chi_nhanh=chi_nhanh, ds_chi_nhanh=ds_chi_nhanh)
@app.route("/them_taikhoan", methods=["GET", "POST"])
def them_taikhoan():
    message = ""
    tai_khoan = None
    ma_tk = ten_tk = loai_tk = ""
    so_du = 0

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        ma_tk = request.form["MaTK"].strip()
        ten_tk = request.form.get("TenTK", "").strip()
        loai_tk = request.form.get("LoaiTK", "").strip()
        try:
            so_du = int(request.form.get("SoDu", 0))
        except ValueError:
            so_du = None

        # Kiểm tra ràng buộc dữ liệu
        if not (ma_tk and ten_tk and loai_tk and so_du is not None):
            message = "Vui lòng nhập đầy đủ thông tin hợp lệ."
            tai_khoan = {"MaTK": ma_tk, "TenTK": ten_tk, "LoaiTK": loai_tk, "SoDu": so_du if so_du else 0}
        else:
            # Kiểm tra tài khoản đã tồn tại chưa
            cursor.execute("SELECT * FROM TaiKhoan WHERE MaTK = ?", (ma_tk,))
            existing = cursor.fetchone()

            if existing:
                message = "Mã tài khoản đã tồn tại. Vui lòng dùng mã khác."
                tai_khoan = {"MaTK": ma_tk, "TenTK": ten_tk, "LoaiTK": loai_tk, "SoDu": so_du}
            else:
                try:
                    cursor.execute("""
                        INSERT INTO TaiKhoan (MaTK, TenTK, LoaiTK, SoDu) VALUES (?, ?, ?, ?)
                    """, (ma_tk, ten_tk, loai_tk, so_du))
                    conn.commit()
                    message = "Thêm tài khoản thành công!"
                    cursor.execute("SELECT * FROM TaiKhoan WHERE MaTK = ?", (ma_tk,))
                    tai_khoan = cursor.fetchone()
                except sqlite3.IntegrityError:
                    message = "Lỗi: Mã tài khoản không hợp lệ hoặc bị trùng."
                    tai_khoan = {"MaTK": ma_tk, "TenTK": ten_tk, "LoaiTK": loai_tk, "SoDu": so_du}

    # Lấy danh sách tài khoản để hiển thị
    cursor.execute("SELECT * FROM TaiKhoan")
    ds_tai_khoan = cursor.fetchall()

    conn.close()
    return render_template("them_taikhoan.html", message=message, tai_khoan=tai_khoan, ds_tai_khoan=ds_tai_khoan)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)