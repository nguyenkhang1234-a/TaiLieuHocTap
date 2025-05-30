from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

class DoThi:
    def __init__(self):
        self.danh_sach_ke = {}
    def them_canh(self, v, w):
        if v not in self.danh_sach_ke:
            self.danh_sach_ke[v] = []
        self.danh_sach_ke[v].append(w)
    def lay_ke(self, v):
        return self.danh_sach_ke.get(v, [])

def bfs(do_thi, diem_bat_dau, diem_ket_thuc, ten_file_ket_qua):
    hang_doi = deque([diem_bat_dau])
    phat_trien = []
    cha = {diem_bat_dau: None}
    da_duyet = {diem_bat_dau}

    with open(ten_file_ket_qua, 'w', encoding='utf-8') as f:
        f.write(f"Điểm bắt đầu: {diem_bat_dau}, Điểm kết thúc: {diem_ket_thuc}\n")
        f.write(f"{'Phát triển TT':<15}{'Trạng thái kề':<20}{'Danh sách Q':<30}{'Danh sách L'}\n")
        f.write(f"{'':<15}{'':<20}{'':<30}{','.join(map(str, hang_doi))}\n")

        while hang_doi:
            hien_tai = hang_doi.popleft()
            trang_thai_ke = do_thi.lay_ke(hien_tai)

            for ke in trang_thai_ke:
                if ke not in da_duyet:
                    da_duyet.add(ke)
                    hang_doi.append(ke)
                    cha[ke] = hien_tai

            phat_trien.append(hien_tai)
            danh_sach_q = sorted(da_duyet)

            if hien_tai == diem_ket_thuc:
                f.write(f"{hien_tai:<15}{'TTKT -> Dừng':<30}\n")
                break
            else: 
                f.write(f"{hien_tai:<15}{','.join(trang_thai_ke):<20}{','.join(danh_sach_q):<30}{','.join(map(str, hang_doi))}\n")

        if diem_ket_thuc in cha:
            duong_di = []
            current = diem_ket_thuc
            while current is not None:
                duong_di.insert(0, current)
                current = cha[current]
                
            f.write("Đường đi từ điểm bắt đầu đến điểm kết thúc: " + " -> ".join(duong_di) + "\n")
            return duong_di

    f.write("Không tìm thấy đường đi từ điểm bắt đầu đến điểm kết thúc.\n")
    return None

def doc_do_thi(duong_dan_file):
    do_thi = DoThi()
    with open(duong_dan_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        try:
            diem_bat_dau, diem_ket_thuc = lines[0].strip().split(" ")
        except ValueError:
            raise ValueError("Dòng đầu tiên trong tệp phải có định dạng 'diem_bat_dau diem_ket_thuc'.")

        for line in lines[1:]:
            parts = line.strip().split()
            v = parts[0]
            for w in parts[1:]:
                do_thi.them_canh(v, w)

    return do_thi, diem_bat_dau, diem_ket_thuc

def ve_do_thi(do_thi, duong_di=None):
    G = nx.DiGraph()

    for dinh in do_thi.danh_sach_ke:
        for ke in do_thi.danh_sach_ke[dinh]:
            G.add_edge(dinh, ke)

    pos = nx.spring_layout(G, seed=42)
    node_colors = ['cyan' if node in duong_di else 'pink' for node in G.nodes]
    edge_colors = ['red' if (u, v) in zip(duong_di, duong_di[1:]) else 'black' for u, v in G.edges]

    plt.figure(figsize=(9, 7))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color=edge_colors,
            node_size=2500, font_size=14, font_weight='bold', width=2)
    plt.title("Đồ thị & Đường đi (nếu có)", fontsize=16)
    plt.show()

if __name__ == "__main__":
    do_thi, diem_bat_dau, diem_ket_thuc = doc_do_thi('input.txt')
    duong_di = bfs(do_thi, diem_bat_dau, diem_ket_thuc, 'output.txt')
    ve_do_thi(do_thi, duong_di)
