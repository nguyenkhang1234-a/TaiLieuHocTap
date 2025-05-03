from flask import Flask, render_template, request, jsonify
import pyodbc

app = Flask(__name__)

conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=TAHO\\SQLEXPRESS;"
    "DATABASE=BankingDB;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(conn_str)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/taikhoan", methods=["GET", "POST"])
def thong_tin_tai_khoan():
    if request.method == 'POST':
        matk = request.form.get("MaTK")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM GiaoDich WHERE MaTK = ?", matk)
            so_lan_gd = cursor.fetchone()[0]
            
            cursor.execute("SELECT TenTK FROM TaiKhoan WHERE MaTK = ?", (matk,))
            row = cursor.fetchone()
            if not row:
                return render_template("taikhoan.html", thong_tin=None, error="Không tìm thấy tài khoản.")
            tentk = row[0]
            
            cursor.execute("SELECT ISNULL(SUM(SoTien), 0) FROM GiaoDich WHERE MaTK = ? AND LoaiGD = 1", matk)
            tong_nap = cursor.fetchone()[0]

            cursor.execute("SELECT ISNULL(SUM(SoTien), 0) FROM GiaoDich WHERE MaTK = ? AND LoaiGD = 2", matk)
            tong_rut = cursor.fetchone()[0]

            cursor.execute("""
                SELECT DISTINCT c.TenCN FROM GiaoDich g
                JOIN ChiNhanh c ON g.MaCN = c.MaCN
                WHERE g.MaTK = ?
            """, matk)
            chi_nhanh = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT ISNULL(SUM(p.SoTienPhat), 0)
                FROM PhatSinh p
                JOIN GiaoDich g ON p.MaGD = g.MaGD
                WHERE g.MaTK = ?
            """, matk)
            tong_phi = cursor.fetchone()[0]

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
    return render_template("taikhoan.html")

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

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM TaiKhoan WHERE MaTK = ?", (matk,))
            if cursor.fetchone()[0] == 0:
                return render_template("giaodich.html", error="Tài khoản không tồn tại.")

            cursor.execute("SELECT COUNT(*) FROM ChiNhanh WHERE MaCN = ?", (macn,))
            if cursor.fetchone()[0] == 0:
                return render_template("giaodich.html", error="Chi nhánh không tồn tại.")

            cursor.execute("""
                INSERT INTO GiaoDich (MaGD, MaTK, MaCN, LoaiGD, SoTien, NgayGD)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (magd, matk, macn, loai_gd, sotien, ngay))

            if loai_gd == 1:
                cursor.execute("UPDATE TaiKhoan SET SoDu += ? WHERE MaTK = ?", (sotien, matk))
            elif loai_gd in [2, 3]:
                cursor.execute("UPDATE TaiKhoan SET SoDu -= ? WHERE MaTK = ?", (sotien, matk))

            conn.commit()
            return render_template("giaodich.html", message="Thêm giao dịch thành công!")

        except Exception as e:
            return render_template("giaodich.html", error=str(e))
        
    return render_template("giaodich.html")
@app.route("/phatsinh", methods=["GET", "POST"])
def danh_sach_phat_sinh():
    if request.method == 'POST':
        maphat = request.form.get("MaPhat")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MaPhat, DaThanhToan FROM PhatSinh WHERE MaPhat = ?", (maphat,))
            row = cursor.fetchone()
            if not row:
                return render_template("phatsinh.html", thong_tin=None, error="Không tìm thấy phát sinh.")

            if row[1] == 0:
                cursor.execute("DELETE FROM PhatSinh WHERE MaPhat = ?", (maphat,))
                conn.commit()

                cursor.execute("SELECT MaPhat, MaGD, SoTienPhat, DaThanhToan FROM PhatSinh WHERE DaThanhToan = 0")
                data = cursor.fetchall()
                return render_template("phatsinh.html", records=data, message="Phát sinh đã được xóa thành công!")
            else:
                return render_template("phatsinh.html", thong_tin=None, error="Không thể xóa: Phát sinh đã thanh toán.")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT MaPhat, MaGD, SoTienPhat, DaThanhToan FROM PhatSinh WHERE DaThanhToan = 0")
    data = cursor.fetchall()
    return render_template("phatsinh.html", records=data)

@app.route("/chinhanh", methods=["GET", "POST"])
def thong_tin_chi_nhanh():
    if request.method == 'POST':
        machinanh = request.form.get("MaCN")
        try:
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

    if request.method == "POST":
        matk = request.form.get("MaTK")

        if request.form.get("action") == "tim":
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT TenTK, LoaiTK FROM TaiKhoan WHERE MaTK = ?", (matk,))
                row = cursor.fetchone()
                if row:
                    thong_tin = {"MaTK": matk, "TenTK": row[0], "LoaiTK": row[1]}
                    show_update_form = True
                else:
                    error = "Không tìm thấy tài khoản."
            except Exception as e:
                error = f"Lỗi khi tìm: {e}"

        elif request.form.get("action") == "capnhat":
            try:
                ten_moi = request.form.get("TenTK")
                loai_moi = request.form.get("LoaiTK")
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE TaiKhoan 
                    SET TenTK = ?, LoaiTK = ? 
                    WHERE MaTK = ?
                """, (ten_moi, loai_moi, matk))
                conn.commit()

                message = "Cập nhật tài khoản thành công!"
                thong_tin = {"MaTK": matk, "TenTK": ten_moi, "LoaiTK": loai_moi}
                show_update_form = True
            except Exception as e:
                error = f"Lỗi khi cập nhật: {e}"

    if show_update_form:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MaTK, TenTK, LoaiTK FROM TaiKhoan ORDER BY MaTK")
            danh_sach_tk = cursor.fetchall()
        except Exception as e:
            error = f"Lỗi khi tải danh sách tài khoản: {e}"

    return render_template("capnhat.html",
                           thong_tin=thong_tin,
                           message=message,
                           error=error,
                           show_update_form=show_update_form,
                           danh_sach_tk=danh_sach_tk)

@app.route("/trungbinhcao", methods=["GET"])
def tai_khoan_trung_binh_cao():
    try:
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
        return render_template("trungbinhcao.html", data=data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)