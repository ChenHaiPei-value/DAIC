#!/usr/bin/env python3
"""
具身智能平台演示脚本

这个脚本演示了DAIC具身智能平台的核心功能：
1. AI机器人设计
2. 物理仿真验证
3. 3D打印集成
4. 供应链对接
"""

import time
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import random

@dataclass
class RobotComponent:
    """机器人组件"""
    name: str
    material: str
    volume: float  # cm³
    weight: float  # grams
    cost: float    # USD
    
@dataclass
class RobotDesign:
    """机器人设计"""
    name: str
    purpose: str
    components: List[RobotComponent]
    total_cost: float
    estimated_print_time: float  # hours
    performance_score: float
    
class RobotDesignEngine:
    """AI机器人设计引擎"""
    
    def __init__(self):
        self.material_costs = {
            "PLA": 0.02,      # USD per gram
            "PETG": 0.03,
            "ABS": 0.025,
            "TPU": 0.05,
            "Nylon": 0.06,
            "Resin": 0.10
        }
        
        self.component_templates = {
            "arm": ["shoulder", "upper_arm", "elbow", "forearm", "wrist", "gripper"],
            "leg": ["hip", "thigh", "knee", "shin", "ankle", "foot"],
            "torso": ["base", "body", "neck", "head"],
            "sensor": ["camera", "lidar", "imu", "ultrasonic"]
        }
    
    def generate_robot_design(self, requirements: Dict) -> RobotDesign:
        """根据需求生成机器人设计"""
        print(f"🎯 开始设计机器人: {requirements['name']}")
        print(f"   用途: {requirements['purpose']}")
        print(f"   预算: ${requirements['budget']}")
        print(f"   重量限制: {requirements['weight_limit']}g")
        
        # 1. 确定机器人类型和组件
        robot_type = self.determine_robot_type(requirements)
        components = self.generate_components(robot_type, requirements)
        
        # 2. 计算总成本
        total_cost = sum(comp.cost for comp in components)
        
        # 3. 估算打印时间
        print_time = self.estimate_print_time(components)
        
        # 4. 评估性能
        performance = self.evaluate_performance(components, requirements)
        
        design = RobotDesign(
            name=requirements['name'],
            purpose=requirements['purpose'],
            components=components,
            total_cost=total_cost,
            estimated_print_time=print_time,
            performance_score=performance
        )
        
        print(f"✅ 设计完成!")
        print(f"   总成本: ${total_cost:.2f}")
        print(f"   打印时间: {print_time:.1f}小时")
        print(f"   性能评分: {performance:.2f}/100")
        
        return design
    
    def determine_robot_type(self, requirements: Dict) -> str:
        """确定机器人类型"""
        purpose = requirements['purpose'].lower()
        
        if any(word in purpose for word in ['arm', 'grip', 'pick', 'place']):
            return "arm"
        elif any(word in purpose for word in ['walk', 'move', 'mobile', 'leg']):
            return "leg"
        elif any(word in purpose for word in ['inspect', 'sense', 'detect']):
            return "sensor"
        else:
            return "general"
    
    def generate_components(self, robot_type: str, requirements: Dict) -> List[RobotComponent]:
        """生成组件列表"""
        components = []
        
        # 根据机器人类型选择组件模板
        if robot_type == "arm":
            component_names = self.component_templates["arm"]
        elif robot_type == "leg":
            component_names = self.component_templates["leg"]
        elif robot_type == "sensor":
            component_names = self.component_templates["sensor"]
        else:
            component_names = self.component_templates["torso"]
        
        # 为每个组件生成具体参数
        for comp_name in component_names:
            # 选择材料
            material = self.select_material(comp_name, requirements)
            
            # 计算体积和重量
            volume = self.calculate_volume(comp_name, requirements)
            weight = volume * 1.25  # 假设密度为1.25g/cm³
            
            # 计算成本
            material_cost_per_gram = self.material_costs[material]
            cost = weight * material_cost_per_gram
            
            component = RobotComponent(
                name=comp_name,
                material=material,
                volume=volume,
                weight=weight,
                cost=cost
            )
            
            components.append(component)
        
        return components
    
    def select_material(self, component_name: str, requirements: Dict) -> str:
        """选择材料"""
        # 简单的材料选择逻辑
        if "gripper" in component_name or "foot" in component_name:
            return "TPU"  # 需要柔韧性
        elif any(word in component_name for word in ['joint', 'bearing', 'moving']):
            return "Nylon"  # 需要耐磨性
        elif requirements.get('environment') == 'outdoor':
            return "PETG"  # 耐候性好
        else:
            return "PLA"  # 通用材料
    
    def calculate_volume(self, component_name: str, requirements: Dict) -> float:
        """计算组件体积"""
        # 基于组件名称和需求的简单体积估算
        base_volumes = {
            "small": 10,   # cm³
            "medium": 50,
            "large": 200
        }
        
        size_factor = requirements.get('size', 'medium')
        base_volume = base_volumes.get(size_factor, 50)
        
        # 根据组件类型调整
        if "base" in component_name or "body" in component_name:
            return base_volume * 2
        elif any(word in component_name for word in ['arm', 'leg', 'thigh']):
            return base_volume * 1.5
        elif any(word in component_name for word in ['wrist', 'ankle', 'neck']):
            return base_volume * 0.5
        else:
            return base_volume
    
    def estimate_print_time(self, components: List[RobotComponent]) -> float:
        """估算打印时间"""
        # 假设打印速度为10cm³/小时
        total_volume = sum(comp.volume for comp in components)
        return total_volume / 10
    
    def evaluate_performance(self, components: List[RobotComponent], requirements: Dict) -> float:
        """评估性能"""
        total_weight = sum(comp.weight for comp in components)
        total_cost = sum(comp.cost for comp in components)
        
        # 简单的性能评分算法
        weight_score = max(0, 100 - (total_weight / requirements['weight_limit'] * 100))
        cost_score = max(0, 100 - (total_cost / requirements['budget'] * 100))
        
        # 材料多样性加分
        materials = set(comp.material for comp in components)
        material_score = len(materials) * 10
        
        # 综合评分
        performance = (weight_score * 0.4 + cost_score * 0.4 + material_score * 0.2)
        
        return min(100, performance)

class SupplyChainManager:
    """供应链管理器"""
    
    def __init__(self):
        self.suppliers = {
            "PLA": ["Supplier_A", "Supplier_B", "Supplier_C"],
            "PETG": ["Supplier_D", "Supplier_E"],
            "ABS": ["Supplier_F"],
            "TPU": ["Supplier_G", "Supplier_H"],
            "Nylon": ["Supplier_I"],
            "Resin": ["Supplier_J"]
        }
        
        self.material_prices = {
            "PLA": {"Supplier_A": 0.019, "Supplier_B": 0.021, "Supplier_C": 0.020},
            "PETG": {"Supplier_D": 0.029, "Supplier_E": 0.031},
            "ABS": {"Supplier_F": 0.024},
            "TPU": {"Supplier_G": 0.049, "Supplier_H": 0.051},
            "Nylon": {"Supplier_I": 0.059},
            "Resin": {"Supplier_J": 0.099}
        }
    
    def source_materials(self, design: RobotDesign, location: str) -> Dict:
        """采购材料"""
        print(f"📦 开始采购材料...")
        
        material_requirements = {}
        for component in design.components:
            if component.material not in material_requirements:
                material_requirements[component.material] = 0
            material_requirements[component.material] += component.weight
        
        orders = []
        total_cost = 0
        
        for material, weight in material_requirements.items():
            # 选择最优供应商
            supplier, price = self.select_best_supplier(material, weight, location)
            
            order_cost = weight * price
            total_cost += order_cost
            
            orders.append({
                "material": material,
                "weight": weight,
                "supplier": supplier,
                "unit_price": price,
                "total_cost": order_cost,
                "estimated_delivery": self.estimate_delivery(supplier, location)
            })
            
            print(f"   📍 {material}: {weight:.1f}g from {supplier} @ ${price:.3f}/g = ${order_cost:.2f}")
        
        print(f"✅ 采购完成! 总材料成本: ${total_cost:.2f}")
        
        return {
            "orders": orders,
            "total_material_cost": total_cost,
            "estimated_total_cost": design.total_cost + total_cost
        }
    
    def select_best_supplier(self, material: str, weight: float, location: str) -> Tuple[str, float]:
        """选择最优供应商"""
        if material not in self.suppliers:
            raise ValueError(f"未知材料: {material}")
        
        suppliers = self.suppliers[material]
        
        # 简单的选择逻辑：价格最低
        best_supplier = None
        best_price = float('inf')
        
        for supplier in suppliers:
            price = self.material_prices[material][supplier]
            if price < best_price:
                best_price = price
                best_supplier = supplier
        
        return best_supplier, best_price
    
    def estimate_delivery(self, supplier: str, location: str) -> str:
        """估算交付时间"""
        # 简单的交付时间估算
        delivery_times = {
            "local": "1-2天",
            "regional": "3-5天",
            "national": "5-7天",
            "international": "7-14天"
        }
        
        # 这里简化处理，实际应该根据供应商和位置计算
        return delivery_times["regional"]

class PrintingManager:
    """3D打印管理器"""
    
    def __init__(self):
        self.printers = [
            {"id": "PR001", "type": "FDM", "material": ["PLA", "PETG", "ABS"], "status": "idle"},
            {"id": "PR002", "type": "FDM", "material": ["PLA", "PETG", "TPU"], "status": "idle"},
            {"id": "PR003", "type": "SLA", "material": ["Resin"], "status": "idle"},
            {"id": "PR004", "type": "FDM", "material": ["Nylon", "PETG"], "status": "busy"}
        ]
    
    def schedule_printing(self, design: RobotDesign, material_orders: List[Dict]) -> Dict:
        """安排打印任务"""
        print(f"🖨️  安排3D打印任务...")
        
        print_jobs = []
        available_printers = [p for p in self.printers if p["status"] == "idle"]
        
        # 按材料分组组件
        components_by_material = {}
        for component in design.components:
            if component.material not in components_by_material:
                components_by_material[component.material] = []
            components_by_material[component.material].append(component)
        
        # 分配打印机
        for material, components in components_by_material.items():
            # 查找支持该材料的空闲打印机
            suitable_printers = [
                p for p in available_printers 
                if material in p["material"]
            ]
            
            if not suitable_printers:
                print(f"   ⚠️  警告: 没有找到支持{material}的空闲打印机")
                continue
            
            printer = suitable_printers[0]
            
            # 计算打印时间
            total_volume = sum(comp.volume for comp in components)
            print_time = total_volume / 10  # 假设10cm³/小时
            
            print_job = {
                "printer_id": printer["id"],
                "printer_type": printer["type"],
                "material": material,
                "components": [comp.name for comp in components],
                "total_volume": total_volume,
                "estimated_time": print_time,
                "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "scheduled"
            }
            
            print_jobs.append(print_job)
            
            print(f"   🖨️  {material}组件: {len(components)}个部件在{printer['id']}上打印")
            print(f"       体积: {total_volume:.1f}cm³, 时间: {print_time:.1f}小时")
        
        total_print_time = sum(job["estimated_time"] for job in print_jobs)
        
        print(f"✅ 打印任务安排完成!")
        print(f"   总打印时间: {total_print_time:.1f}小时")
        print(f"   使用打印机: {len(print_jobs)}台")
        
        return {
            "print_jobs": print_jobs,
            "total_print_time": total_print_time,
            "estimated_completion": self.calculate_completion_time(total_print_time)
        }
    
    def calculate_completion_time(self, total_hours: float) -> str:
        """计算完成时间"""
        # 假设每天工作8小时
        days = total_hours / 8
        if days <= 1:
            return "今天内完成"
        elif days <= 2:
            return "1-2天内完成"
        else:
            return f"{int(days)}天内完成"

def main():
    """主演示函数"""
    print("=" * 60)
    print("🤖 DAIC 具身智能平台演示")
    print("=" * 60)
    
    # 1. 定义机器人需求
    requirements = {
        "name": "Demo_Robot_Arm",
        "purpose": "轻型物品抓取和放置",
        "budget": 150.0,      # USD
        "weight_limit": 500,  # grams
        "size": "medium",
        "environment": "indoor"
    }
    
    print("\n1. 🎯 机器人需求分析")
    print(json.dumps(requirements, indent=2, ensure_ascii=False))
    
    # 2. AI设计机器人
    print("\n2. 🎨 AI机器人设计")
    design_engine = RobotDesignEngine()
    robot_design = design_engine.generate_robot_design(requirements)
    
    print("\n   设计详情:")
    for i, component in enumerate(robot_design.components, 1):
        print(f"     {i}. {component.name}: {component.material}, "
              f"{component.volume:.1f}cm³, {component.weight:.1f}g, ${component.cost:.2f}")
    
    # 3. 供应链采购
    print("\n3. 📦 供应链材料采购")
    supply_chain = SupplyChainManager()
    procurement = supply_chain.source_materials(robot_design, "Shanghai")
    
    # 4. 3D打印安排
    print("\n4. 🖨️  3D打印任务安排")
    printing_manager = PrintingManager()
    printing_schedule = printing_manager.schedule_printing(
        robot_design, 
        procurement["orders"]
    )
    
    # 5. 总结
    print("\n" + "=" * 60)
    print("📊 项目总结")
    print("=" * 60)
    
    total_cost = procurement["estimated_total_cost"]
    budget_utilization = (total_cost / requirements["budget"]) * 100
    
    print(f"🤖 机器人名称: {robot_design.name}")
    print(f"🎯 设计用途: {robot_design.purpose}")
    print(f"💰 总成本: ${total_cost:.2f} (预算利用率: {budget_utilization:.1f}%)")
    print(f"⚖️  总重量: {sum(c.weight for c in robot_design.components):.1f}g")
    print(f"⏱️  总制造时间: {printing_schedule['total_print_time']:.1f}小时")
    print(f"📈 性能评分: {robot_design.performance_score:.2f}/100")
    print(f"📅 预计完成: {printing_schedule['estimated_completion']}")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成!")
    print("=" * 60)
    
    # 保存设计文件
    design_data = {
        "requirements": requirements,
        "design": {
            "name": robot_design.name,
            "purpose": robot_design.purpose,
            "total_cost": robot_design.total_cost,
            "estimated_print_time": robot_design.estimated_print_time,
            "performance_score": robot_design.performance_score,
            "components": [
                {
                    "name": comp.name,
                    "material": comp.material,
                    "volume": comp.volume,
                    "weight": comp.weight,
                    "cost": comp.cost
                }
                for comp in robot_design.components
            ]
        },
        "procurement": procurement,
        "printing_schedule": printing_schedule,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 保存到文件
    output_file = "robot_design_demo.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(design_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 设计文件已保存: {output_file}")
    
    return design_data

if __name__ == "__main__":
    main()
