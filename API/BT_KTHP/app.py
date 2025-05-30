from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
DB_NAME = 'university.db'

def init_db():
    conn = sqlite3.connect('university.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tblBoMon (
            MaBM TEXT PRIMARY KEY,
            TenBM TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tblGV (
            MaGV TEXT PRIMARY KEY,
            TenGV TEXT NOT NULL,
            BoMon TEXT,
            GioiTinh TEXT,
            DiaChi TEXT,
            SoDT TEXT,
            FOREIGN KEY (BoMon) REFERENCES tblBoMon(MaBM)
        )
    ''')

    ds_bomon = [
        ('BM01', 'Công nghệ phần mềm'),
        ('BM02', 'Mạng máy tính'),
        ('BM03', 'Hệ thống thông tin'),
        ('BM04', 'Trí tuệ nhân tạo'),
        ('BM05', 'Khoa học máy tính'),
        ('BM06', 'Kỹ thuật máy tính')
    ]
    cursor.executemany('INSERT OR IGNORE INTO tblBoMon (MaBM, TenBM) VALUES (?, ?)', ds_bomon)

    ds_gv = [
        # Công nghệ phần mềm
        ('GV001', 'Nguyễn Văn An', 'BM01', 'Nam', '15 Láng Hạ, Hà Nội', '0901000001'),
        ('GV002', 'Trần Thị Bình', 'BM01', 'Nữ', '23 Trần Phú, Hà Nội', '0901000002'),
        ('GV003', 'Lê Văn Cường', 'BM01', 'Nam', '45 Nguyễn Trãi, Hà Nội', '0901000003'),
        ('GV004', 'Phạm Thị Duyên', 'BM01', 'Nữ', '12 Giải Phóng, Hà Nội', '0901000004'),
        ('GV005', 'Vũ Minh Đức', 'BM01', 'Nam', '78 Kim Mã, Hà Nội', '0901000005'),
        ('GV006', 'Ngô Thanh Hà', 'BM01', 'Nữ', '34 Bạch Mai, Hà Nội', '0901000006'),
        ('GV007', 'Đinh Quang Hưng', 'BM01', 'Nam', '56 Tây Sơn, Hà Nội', '0901000007'),
        ('GV008', 'Hoàng Thị Hạnh', 'BM01', 'Nữ', '29 Đội Cấn, Hà Nội', '0901000008'),
        ('GV009', 'Lý Văn Kiên', 'BM01', 'Nam', '88 Hoàng Quốc Việt, Hà Nội', '0901000009'),
        ('GV010', 'Tạ Thị Lan', 'BM01', 'Nữ', '101 Cầu Giấy, Hà Nội', '0901000010'),

        # Mạng máy tính
        ('GV011', 'Bùi Anh Tuấn', 'BM02', 'Nam', '32 Điện Biên Phủ, TP.HCM', '0911000001'),
        ('GV012', 'Đặng Thị Mai', 'BM02', 'Nữ', '25 Lê Lợi, TP.HCM', '0911000002'),
        ('GV013', 'Nguyễn Hoàng Long', 'BM02', 'Nam', '77 Nguyễn Huệ, TP.HCM', '0911000003'),
        ('GV014', 'Phan Thị Hương', 'BM02', 'Nữ', '68 Võ Văn Tần, TP.HCM', '0911000004'),
        ('GV015', 'Trịnh Văn Sơn', 'BM02', 'Nam', '12 Lý Tự Trọng, TP.HCM', '0911000005'),
        ('GV016', 'Cao Mỹ Duyên', 'BM02', 'Nữ', '45 Nguyễn Thị Minh Khai, TP.HCM', '0911000006'),
        ('GV017', 'Lương Văn Đạt', 'BM02', 'Nam', '56 Hai Bà Trưng, TP.HCM', '0911000007'),
        ('GV018', 'Hồ Thị Thanh', 'BM02', 'Nữ', '29 Cách Mạng Tháng Tám, TP.HCM', '0911000008'),
        ('GV019', 'Phạm Văn Tình', 'BM02', 'Nam', '63 Nam Kỳ Khởi Nghĩa, TP.HCM', '0911000009'),
        ('GV020', 'Đào Thị Yến', 'BM02', 'Nữ', '90 Lê Duẩn, TP.HCM', '0911000010'),

        # Hệ thống thông tin
        ('GV021', 'Trần Văn Minh', 'BM03', 'Nam', '21 Nguyễn Văn Linh, Đà Nẵng', '0921000001'),
        ('GV022', 'Lê Thị Thu', 'BM03', 'Nữ', '47 Hùng Vương, Đà Nẵng', '0921000002'),
        ('GV023', 'Phan Minh Trí', 'BM03', 'Nam', '89 Lê Duẩn, Đà Nẵng', '0921000003'),
        ('GV024', 'Nguyễn Thị Hà', 'BM03', 'Nữ', '32 Trưng Nữ Vương, Đà Nẵng', '0921000004'),
        ('GV025', 'Võ Văn Bình', 'BM03', 'Nam', '65 Nguyễn Hữu Thọ, Đà Nẵng', '0921000005'),
        ('GV026', 'Đinh Thị Mai', 'BM03', 'Nữ', '11 Bạch Đằng, Đà Nẵng', '0921000006'),
        ('GV027', 'Hoàng Văn Long', 'BM03', 'Nam', '88 Hoàng Diệu, Đà Nẵng', '0921000007'),
        ('GV028', 'Trịnh Thị Ngọc', 'BM03', 'Nữ', '24 Phan Châu Trinh, Đà Nẵng', '0921000008'),
        ('GV029', 'Lê Văn Khánh', 'BM03', 'Nam', '39 Lý Thường Kiệt, Đà Nẵng', '0921000009'),
        ('GV030', 'Tống Thị Thanh', 'BM03', 'Nữ', '58 Nguyễn Chí Thanh, Đà Nẵng', '0921000010'),

        # Trí tuệ nhân tạo
        ('GV031', 'Nguyễn Văn Toàn', 'BM04', 'Nam', '12 Nguyễn Phong Sắc, Hà Nội', '0931000001'),
        ('GV032', 'Trần Thị Lệ', 'BM04', 'Nữ', '45 Hoàng Văn Thái, Hà Nội', '0931000002'),
        ('GV033', 'Phạm Văn Khôi', 'BM04', 'Nam', '78 Trần Duy Hưng, Hà Nội', '0931000003'),
        ('GV034', 'Đỗ Thị Mai', 'BM04', 'Nữ', '29 Đường Láng, Hà Nội', '0931000004'),
        ('GV035', 'Lê Đức Thắng', 'BM04', 'Nam', '87 Chùa Bộc, Hà Nội', '0931000005'),
        ('GV036', 'Nguyễn Thị Tuyết', 'BM04', 'Nữ', '63 Thái Hà, Hà Nội', '0931000006'),
        ('GV037', 'Vũ Minh Quang', 'BM04', 'Nam', '101 Xã Đàn, Hà Nội', '0931000007'),
        ('GV038', 'Bùi Thị Yến', 'BM04', 'Nữ', '34 Lê Trọng Tấn, Hà Nội', '0931000008'),
        ('GV039', 'Trịnh Văn Hậu', 'BM04', 'Nam', '56 Nguyễn Chí Thanh, Hà Nội', '0931000009'),
        ('GV040', 'Lại Thị Ngân', 'BM04', 'Nữ', '23 Hào Nam, Hà Nội', '0931000010'),

        # Khoa học máy tính
        ('GV041', 'Hoàng Văn Thành', 'BM05', 'Nam', '17 Cách Mạng Tháng 8, TP.HCM', '0941000001'),
        ('GV042', 'Phan Thị Lan', 'BM05', 'Nữ', '45 Trần Quang Khải, TP.HCM', '0941000002'),
        ('GV043', 'Nguyễn Hữu Phúc', 'BM05', 'Nam', '89 Lê Thánh Tôn, TP.HCM', '0941000003'),
        ('GV044', 'Trịnh Thị Hoa', 'BM05', 'Nữ', '33 Nguyễn Đình Chiểu, TP.HCM', '0941000004'),
        ('GV045', 'Đặng Minh Hùng', 'BM05', 'Nam', '12 Phạm Ngọc Thạch, TP.HCM', '0941000005'),
        ('GV046', 'Lê Thị Nhung', 'BM05', 'Nữ', '77 Nguyễn Thị Minh Khai, TP.HCM', '0941000006'),
        ('GV047', 'Vũ Văn Quân', 'BM05', 'Nam', '43 Võ Thị Sáu, TP.HCM', '0941000007'),
        ('GV048', 'Ngô Thị Huyền', 'BM05', 'Nữ', '21 Bùi Thị Xuân, TP.HCM', '0941000008'),
        ('GV049', 'Trần Văn Tùng', 'BM05', 'Nam', '60 Nguyễn Trãi, TP.HCM', '0941000009'),
        ('GV050', 'Mai Thị Hạnh', 'BM05', 'Nữ', '28 Sư Vạn Hạnh, TP.HCM', '0941000010'),

        # Kỹ thuật máy tính
        ('GV051', 'Lê Anh Vũ', 'BM06', 'Nam', '36 Trần Cao Vân, Đà Nẵng', '0951000001'),
        ('GV052', 'Đinh Thị Dung', 'BM06', 'Nữ', '67 Nguyễn Văn Linh, Đà Nẵng', '0951000002'),
        ('GV053', 'Nguyễn Hữu Lộc', 'BM06', 'Nam', '11 Điện Biên Phủ, Đà Nẵng', '0951000003'),
        ('GV054', 'Phạm Thị Thảo', 'BM06', 'Nữ', '89 Hoàng Hoa Thám, Đà Nẵng', '0951000004'),
        ('GV055', 'Hoàng Minh Quân', 'BM06', 'Nam', '23 Lê Đình Dương, Đà Nẵng', '0951000005'),
        ('GV056', 'Trần Thị Vân', 'BM06', 'Nữ', '45 Nguyễn Tri Phương, Đà Nẵng', '0951000006'),
        ('GV057', 'Võ Văn Thắng', 'BM06', 'Nam', '67 Lê Văn Hiến, Đà Nẵng', '0951000007'),
        ('GV058', 'Lý Thị Ngọc', 'BM06', 'Nữ', '38 Hàm Nghi, Đà Nẵng', '0951000008'),
        ('GV059', 'Đào Văn Hùng', 'BM06', 'Nam', '92 Phan Đình Phùng, Đà Nẵng', '0951000009'),
        ('GV060', 'Nguyễn Thị Diễm', 'BM06', 'Nữ', '15 Ông Ích Khiêm, Đà Nẵng', '0951000010'),

    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO tblGV (MaGV, TenGV, BoMon, GioiTinh, DiaChi, SoDT)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ds_gv)

    conn.commit()
    conn.close()

# API trả về danh sách giảng viên theo tên bộ môn gần đúng
@app.route('/api/giangvien', methods=['GET'])
def tim_giang_vien():
    ten_bm = request.args.get('bomon', '')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT gv.MaGV, gv.TenGV, bm.TenBM, gv.GioiTinh, gv.DiaChi, gv.SoDT
        FROM tblGV gv
        JOIN tblBoMon bm ON gv.BoMon = bm.MaBM
        WHERE bm.TenBM LIKE ?
    ''', (f'%{ten_bm}%',))
    rows = c.fetchall()
    conn.close()

    result = [
        {
            'MaGV': r[0],
            'TenGV': r[1],
            'BoMon': r[2],
            'GioiTinh': r[3],
            'DiaChi': r[4],
            'SoDT': r[5]
        } for r in rows
    ]
    return jsonify(result)

@app.route('/', methods=['GET', 'POST'])
def home():
    search_term = request.form.get('bomon', '')
    result = []

    # Lấy danh sách bộ môn để đưa vào datalist
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT MaBM, TenBM FROM tblBoMon ORDER BY TenBM')
    ds_bomon = c.fetchall()
    conn.close()

    if search_term:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            SELECT gv.MaGV, gv.TenGV, bm.TenBM, gv.GioiTinh, gv.DiaChi, gv.SoDT
            FROM tblGV gv
            JOIN tblBoMon bm ON gv.BoMon = bm.MaBM
            WHERE bm.TenBM LIKE ?
        ''', (f'%{search_term}%',))
        rows = c.fetchall()
        conn.close()

        result = [
            {
                'MaGV': r[0],
                'TenGV': r[1],
                'BoMon': r[2],
                'GioiTinh': r[3],
                'DiaChi': r[4],
                'SoDT': r[5]
            } for r in rows
        ]

    return render_template('index.html', result=result, search_term=search_term, ds_bomon=ds_bomon)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
