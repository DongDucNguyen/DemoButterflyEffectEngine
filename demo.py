import numpy as np
import networkx as nx
import pandas as pd
from datetime import datetime, timedelta

class ButterflyEffectEngine:
    def __init__(self):
        # 1. Khởi tạo Knowledge Graph (Sơ đồ tri thức)
        # Các nút (Nodes) dựa theo tài liệu [cite: 139, 148]
        self.nodes = [
            "Mỏ đồng Chile", "Giá đồng thế giới", "Linh kiện PC", 
            "Trung Quốc", "Pin Lithium", "Vận tải biển", "Lao động"
        ]
        self.node_idx = {node: i for i, node in enumerate(self.nodes)}
        self.graph = self._build_graph()
        # Ma trận kề A đại diện cho các cạnh (Edges) [cite: 149, 172]
        self.adj_matrix = nx.to_numpy_array(self.graph, nodelist=self.nodes)

    def _build_graph(self):
        G = nx.DiGraph()
        # Định nghĩa các mối liên hệ và trọng số ảnh hưởng (Weight)
        edges = [
            ("Mỏ đồng Chile", "Giá đồng thế giới", 0.9),
            ("Giá đồng thế giới", "Linh kiện PC", 0.7),
            ("Giá đồng thế giới", "Pin Lithium", 0.5),
            ("Trung Quốc", "Pin Lithium", 0.6),
            ("Vận tải biển", "Linh kiện PC", 0.4),
            ("Lao động", "Mỏ đồng Chile", 0.8)
        ]
        for u, v, w in edges:
            G.add_edge(u, v, weight=w)
        return G

    def extract_entities_and_sentiment(self, text):
        """Lớp NLP: Trích xuất thực thể và Cảm xúc (Sentiment) [cite: 159, 160]"""
        text_lower = text.lower()
        impacted_node = None
        sentiment = 0

        # NER đơn giản: Tìm nút gốc của sự kiện
        if "chile" in text_lower or "mỏ đồng" in text_lower:
            impacted_node = "Mỏ đồng Chile"
        elif "trung quốc" in text_lower:
            impacted_node = "Trung Quốc"
        elif "vận tải biển" in text_lower or "cảng" in text_lower:
            impacted_node = "Vận tải biển"
        elif "đình công" in text_lower or "lao động" in text_lower:
            impacted_node = "Lao động"

        # Logic Cảm xúc: Tin tiêu cực cho nguồn cung = Giá tăng (Sentiment dương)
        neg_words = ["đình công", "giảm", "khắc nghiệt", "tăng thuế", "thất bại", "ngập lụt", "ùn tắc", "thắt chặt", "thiếu hụt", "bất ổn"]
        pos_words = ["tăng trưởng", "chấm dứt", "thỏa thuận", "mở rộng", "ổn định", "hồi phục", "tăng sản lượng"]

        if any(w in text_lower for w in neg_words):
            sentiment = 1.0 
        elif any(w in text_lower for w in pos_words):
            sentiment = -1.0 
        
        return impacted_node, sentiment

    def gnn_predict(self, source_node, sentiment):
        """Mô phỏng GNN: Lan truyền ảnh hưởng qua ma trận [cite: 150, 171]"""
        n = len(self.nodes)
        h = np.zeros(n)
        h[self.node_idx[source_node]] = sentiment
        
        # Lan truyền H(l+1) = sigma(A.T * H)
        # h1: Ảnh hưởng trực tiếp (1-hop)
        h1 = np.dot(self.adj_matrix.T, h)
        # h2: Ảnh hưởng gián tiếp (2-hop - Hiệu ứng cánh bướm)
        h2 = np.dot(self.adj_matrix.T, h1)
        
        return h1 + h2

    def run_backtest(self, file_path):
        results = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "|" not in line: continue
                date_str, content = line.split("|")
                date_str, content = date_str.strip(), content.strip()
                
                # Bước 1: NLP trích xuất thông tin & Lọc nhiễu 
                node, sentiment = self.extract_entities_and_sentiment(content)
                
                if node and sentiment != 0:
                    # Bước 2: Tính toán dự báo bằng GNN
                    impact_vector = self.gnn_predict(node, sentiment)
                    
                    pc_idx = self.node_idx["Linh kiện PC"]
                    li_idx = self.node_idx["Pin Lithium"]
                    
                    pc_impact = impact_vector[pc_idx]
                    li_impact = impact_vector[li_idx]
                    
                    # Bước 3: Áp dụng độ trễ (Lag time) 14 ngày 
                    impact_date = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
                    
                    if abs(pc_impact) > 0.01 or abs(li_impact) > 0.01:
                        results.append({
                            "Ngày tin": date_str,
                            "Sự kiện gốc": node,
                            "Ngày dự báo": impact_date,
                            "Biến động PC": f"{pc_impact*10:+.1f}%",
                            "Biến động Pin": f"{li_impact*10:+.1f}%"
                        })
        return pd.DataFrame(results)

# Thực thi
engine = ButterflyEffectEngine()
df_report = engine.run_backtest("news.txt")
df_report.to_csv("butterfly_effect_report.csv", index=False)
print(df_report.to_string())