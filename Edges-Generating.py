import networkx as nx
import matplotlib.pyplot as plt

class EconomicKnowledgeGraph:
    def __init__(self):
        # Khởi tạo đồ thị có hướng (DiGraph) để thể hiện luồng ảnh hưởng một chiều
        self.G = nx.DiGraph()

    def add_economic_node(self, node_id, node_type, metadata=None):
        """
        Cơ chế tạo Node: Mỗi nút đại diện cho một thực thể kinh tế [cite: 13]
        - node_type: 'Location', 'Commodity', 'Event', 'Market'
        """
        self.G.add_node(node_id, type=node_type, **(metadata or {}))
        print(f"[Node Created] {node_type}: {node_id}")

    def add_impact_edge(self, source, target, relation_type, weight):
        """
        Cơ chế tạo Edge: Định nghĩa mối quan hệ và trọng số ảnh hưởng [cite: 14]
        - relation_type: 'Supplies', 'Influences', 'Correlates'
        - weight: Độ mạnh của ảnh hưởng (0.0 - 1.0)
        """
        self.G.add_edge(source, target, relation=relation_type, weight=weight)
        print(f"[Edge Created] {source} --({relation_type}, w={weight})--> {target}")

    def visualize_graph(self):
        """Trực quan hóa sơ đồ (Giai đoạn 4: Dashboard) [cite: 18]"""
        plt.figure(figsize=(10, 7))
        pos = nx.spring_layout(self.G, seed=42)
        
        # Vẽ các nút dựa trên loại (màu sắc khác nhau)
        node_colors = []
        for n, data in self.G.nodes(data=True):
            if data['type'] == 'Location': node_colors.append('skyblue')
            elif data['type'] == 'Commodity': node_colors.append('orange')
            else: node_colors.append('lightgreen')

        nx.draw(self.G, pos, with_labels=True, node_color=node_colors, 
                node_size=3000, font_size=10, font_weight='bold', arrowsize=20)
        
        # Hiển thị trọng số trên các cạnh
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels)
        
        plt.title("Mô phỏng Knowledge Graph - Socio-Economic Butterfly Effect")
        plt.show()

# --- THỰC THI TẠO CẤU TRÚC ---
kg = EconomicKnowledgeGraph()

# 1. Tạo các Nút (Nodes) [cite: 13]
kg.add_economic_node("Mỏ đồng Chile", "Location", {"status": "Active"})
kg.add_economic_node("Đồng (Copper)", "Commodity", {"unit": "Tấn"})
kg.add_economic_node("Linh kiện PC", "Market", {"region": "Việt Nam"})
kg.add_economic_node("Đình công", "Event", {"severity": "High"})

# 2. Tạo các Cạnh (Edges) thể hiện logic lan truyền [cite: 14]
# Đình công ảnh hưởng đến hoạt động tại mỏ
kg.add_impact_edge("Đình công", "Mỏ đồng Chile", "Influences", 0.9)
# Mỏ đồng cung cấp nguyên liệu cho thị trường đồng
kg.add_impact_edge("Mỏ đồng Chile", "Đồng (Copper)", "Supplies", 0.85)
# Giá đồng ảnh hưởng trực tiếp đến giá linh kiện PC tại VN [cite: 3]
kg.add_impact_edge("Đồng (Copper)", "Linh kiện PC", "Correlates", 0.7)

# 3. Xuất sơ đồ
kg.visualize_graph()
