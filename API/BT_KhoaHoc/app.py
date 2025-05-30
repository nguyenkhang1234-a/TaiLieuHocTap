from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB_NAME = 'khoahoc.db'

# ======= TẠO CSDL & DỮ LIỆU MẪU =======
def init_db():
    if os.path.exists(DB_NAME):
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE KhoaHoc (
            MaKH TEXT PRIMARY KEY,
            TenKH TEXT,
            MoTa TEXT,
            HocPhi INTEGER,
            HinhThuc TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE HocVien (
            MaHV TEXT PRIMARY KEY,
            TenHV TEXT,
            Email TEXT,
            NgaySinh TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE DangKy (
            MaDK TEXT PRIMARY KEY,
            MaHV TEXT,
            MaKH TEXT,
            NgayDK TEXT,
            TrangThai INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE ThanhToan (
            MaTT TEXT PRIMARY KEY,
            MaDK TEXT,
            SoTien INTEGER,
            DaThanhToan INTEGER
        )
    ''')

    # Thêm dữ liệu mẫu
    c.executemany('INSERT INTO KhoaHoc VALUES (?, ?, ?, ?, ?)', [
        ('KH01', 'Python cơ bản', 'Lập trình căn bản Python', 2500000, 'Online'),
        ('KH02', 'Thiết kế Web', 'HTML/CSS/JS cơ bản', 3000000, 'Offline'),
        ('KH03', 'Phân tích dữ liệu', 'Data Analysis với Pandas', 4000000, 'Online')
    ])
    c.executemany('INSERT INTO HocVien VALUES (?, ?, ?, ?)', [
        ('HV01', 'Nguyễn Văn A', 'a@gmail.com', '2000-01-01'),
        ('HV02', 'Trần Thị B', 'b@gmail.com', '2001-02-02'),
        ('HV03', 'Lê Văn C', 'c@gmail.com', '2002-03-03')
    ])
    c.executemany('INSERT INTO DangKy VALUES (?, ?, ?, ?, ?)', [
        ('DK01', 'HV01', 'KH01', '2024-01-01', 2),
        ('DK02', 'HV01', 'KH02', '2024-03-15', 1),
        ('DK03', 'HV02', 'KH03', '2024-04-01', 0)
    ])
    c.executemany('INSERT INTO ThanhToan VALUES (?, ?, ?, ?)', [
        ('TT01', 'DK01', 2500000, 1),
        ('TT02', 'DK02', 3000000, 1),
        ('TT03', 'DK03', 1000000, 0)
    ])
    conn.commit()
    conn.close()

init_db()

# ============ API ROUTES ============
@app.route('/')
def trang_chu():
    return render_template('trangchu.html')

# 1. Thống kê theo MaHV
@app.route('/thongke')
def thongke():
    MaHV = request.args.get('MaHV', '')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM DangKy WHERE MaHV = ?', (MaHV,))
    so_khoa = c.fetchone()[0]

    c.execute('''
        SELECT SUM(SoTien) FROM ThanhToan
        WHERE MaDK IN (SELECT MaDK FROM DangKy WHERE MaHV = ?) AND DaThanhToan = 1
    ''', (MaHV,))
    tong_tien = c.fetchone()[0] or 0

    c.execute('''
        SELECT KhoaHoc.TenKH FROM DangKy
        JOIN KhoaHoc ON DangKy.MaKH = KhoaHoc.MaKH
        WHERE MaHV = ? AND TrangThai = 2
    ''', (MaHV,))
    da_hoc_xong = [row[0] for row in c.fetchall()]
    conn.close()

    return render_template('thongke.html', MaHV=MaHV, so_khoa=so_khoa,
                           tong_tien=tong_tien, da_hoc_xong=da_hoc_xong)

# 2. Đăng ký khóa học
@app.route('/dangky', methods=['GET', 'POST'])
def dangky():
    if request.method == 'POST':
        MaDK = request.form['MaDK']
        MaHV = request.form['MaHV']
        MaKH = request.form['MaKH']
        NgayDK = request.form['NgayDK']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO DangKy VALUES (?, ?, ?, ?, 0)', (MaDK, MaHV, MaKH, NgayDK))
        conn.commit()
        conn.close()
        return redirect('/dangky')
    return render_template('dangky.html')

# 3. Cập nhật trạng thái học
@app.route('/capnhat', methods=['GET', 'POST'])
def capnhat():
    if request.method == 'POST':
        MaDK = request.form['MaDK']
        TrangThai = int(request.form['TrangThai'])
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('UPDATE DangKy SET TrangThai = ? WHERE MaDK = ?', (TrangThai, MaDK))
        conn.commit()
        conn.close()
        return redirect('/capnhat')
    return render_template('capnhat.html')

# 4. Thêm thanh toán học phí
@app.route('/thanhtoan', methods=['GET', 'POST'])
def thanhtoan():
    if request.method == 'POST':
        MaTT = request.form['MaTT']
        MaDK = request.form['MaDK']
        SoTien = int(request.form['SoTien'])
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT SUM(SoTien) FROM ThanhToan WHERE MaDK = ?', (MaDK,))
        tong_tien = c.fetchone()[0] or 0

        c.execute('SELECT HocPhi FROM DangKy JOIN KhoaHoc ON DangKy.MaKH = KhoaHoc.MaKH WHERE MaDK = ?', (MaDK,))
        hoc_phi = c.fetchone()
        if hoc_phi:
            hoc_phi = hoc_phi[0]
            if tong_tien + SoTien <= hoc_phi:
                da_tt = 1 if tong_tien + SoTien == hoc_phi else 0
                c.execute('INSERT INTO ThanhToan VALUES (?, ?, ?, ?)', (MaTT, MaDK, SoTien, da_tt))
        conn.commit()
        conn.close()
        return redirect('/thanhtoan')
    return render_template('thanhtoan.html')

# 5. Xóa thanh toán nếu DaThanhToan = 0
@app.route('/xoathanhtoan', methods=['GET', 'POST'])
def xoathanhtoan():
    if request.method == 'POST':
        MaTT = request.form['MaTT']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('DELETE FROM ThanhToan WHERE MaTT = ? AND DaThanhToan = 0', (MaTT,))
        conn.commit()
        conn.close()
        return redirect('/xoathanhtoan')
    return render_template('xoathanhtoan.html')

# 6. Liệt kê học viên có tổng thanh toán > 5 triệu
@app.route('/lietke')
def lietke():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT HocVien.MaHV, TenHV, SUM(SoTien) as TongTien
        FROM HocVien
        JOIN DangKy ON HocVien.MaHV = DangKy.MaHV
        JOIN ThanhToan ON DangKy.MaDK = ThanhToan.MaDK
        WHERE DaThanhToan = 1
        GROUP BY HocVien.MaHV
        HAVING TongTien > 5000000
    ''')
    hocviens = c.fetchall()
    conn.close()
    return render_template('lietke.html', hocviens=hocviens)

if __name__ == '__main__':
    app.run(debug=True)
