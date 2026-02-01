"""
RAG Impact Comparison Test
Measures improvement from RAG enhancement
"""

import time
from typing import Dict, List
import json
from datetime import datetime


class RAGComparisonTest:
    """Compare agent performance with and without RAG"""
    
    def __init__(self):
        """Initialize test suite"""
        self.test_queries = [
            {
                "id": 1,
                "question": "What is our current MRR?",
                "category": "Revenue Metrics",
                "complexity": "Simple",
                "requires_rag": True,
                "expected_elements": ["SUM", "billing_cycle", "CASE", "active"]
            },
            {
                "id": 2,
                "question": "Show me revenue by plan tier",
                "category": "Segmentation",
                "complexity": "Medium",
                "requires_rag": True,
                "expected_elements": ["JOIN", "plans", "GROUP BY", "plan_tier"]
            },
            {
                "id": 3,
                "question": "How many active customers do we have?",
                "category": "Customer Metrics",
                "complexity": "Simple",
                "requires_rag": False,
                "expected_elements": ["COUNT", "DISTINCT", "active"]
            },
            {
                "id": 4,
                "question": "What's our monthly churn rate?",
                "category": "Customer Metrics",
                "complexity": "Complex",
                "requires_rag": True,
                "expected_elements": ["cancelled", "end_date", "start_date"]
            },
            {
                "id": 5,
                "question": "Show me customers at high churn risk",
                "category": "Health & Churn",
                "complexity": "Complex",
                "requires_rag": True,
                "expected_elements": ["customer_health", "churn_risk", "high"]
            },
            {
                "id": 6,
                "question": "What's our CAC by marketing channel?",
                "category": "Marketing",
                "complexity": "Complex",
                "requires_rag": True,
                "expected_elements": ["campaigns", "budget", "campaign_attribution"]
            },
            {
                "id": 7,
                "question": "Which features are most popular?",
                "category": "Engagement",
                "complexity": "Medium",
                "requires_rag": False,
                "expected_elements": ["usage_events", "feature_name", "COUNT"]
            },
            {
                "id": 8,
                "question": "Show me MRR trend over last 6 months",
                "category": "Time Series",
                "complexity": "Medium",
                "requires_rag": True,
                "expected_elements": ["GROUP BY", "strftime", "date"]
            }
        ]
    
    def validate_sql(self, sql: str, expected_elements: List[str]) -> Dict:
        """
        Validate SQL contains expected elements
        
        Returns:
            Dict with validation results
        """
        sql_upper = sql.upper()
        
        found_elements = []
        missing_elements = []
        
        for element in expected_elements:
            if element.upper() in sql_upper:
                found_elements.append(element)
            else:
                missing_elements.append(element)
        
        score = len(found_elements) / len(expected_elements) if expected_elements else 1.0
        
        return {
            "score": score,
            "found": found_elements,
            "missing": missing_elements,
            "passed": score >= 0.75  # 75% threshold
        }
    
    def run_test(self, agent, query: Dict, mode: str) -> Dict:
        """
        Run single test query
        
        Args:
            agent: Agent instance (with or without RAG)
            query: Test query dict
            mode: "with_rag" or "without_rag"
            
        Returns:
            Test result dict
        """
        print(f"\n  Testing: {query['question']}")
        
        start_time = time.time()
        
        try:
            result = agent.query(query['question'])
            latency = time.time() - start_time
            
            # Extract SQL from result (implementation depends on your agent)
            # This is a placeholder - adapt to your agent's response format
            sql = result.get('sql', '') or result.get('answer', '')
            
            # Validate SQL
            validation = self.validate_sql(sql, query['expected_elements'])
            
            return {
                "query_id": query['id'],
                "question": query['question'],
                "category": query['category'],
                "complexity": query['complexity'],
                "mode": mode,
                "success": result.get('success', False),
                "latency": latency,
                "sql": sql[:200] + "..." if len(sql) > 200 else sql,
                "validation_score": validation['score'],
                "validation_passed": validation['passed'],
                "found_elements": validation['found'],
                "missing_elements": validation['missing'],
                "retrieved_docs": result.get('retrieved_docs', 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "query_id": query['id'],
                "question": query['question'],
                "mode": mode,
                "success": False,
                "error": str(e),
                "latency": time.time() - start_time,
                "validation_score": 0.0,
                "validation_passed": False
            }
    
    def run_comparison(self, agent_without_rag, agent_with_rag) -> Dict:
        """
        Run full comparison test suite
        
        Returns:
            Comparison results
        """
        print("\n" + "="*60)
        print("RAG COMPARISON TEST")
        print("="*60)
        
        results_without_rag = []
        results_with_rag = []
        
        # Test WITHOUT RAG
        print("\n[1/2] Testing WITHOUT RAG...")
        print("-"*60)
        for query in self.test_queries:
            result = self.run_test(agent_without_rag, query, "without_rag")
            results_without_rag.append(result)
        
        # Test WITH RAG
        print("\n[2/2] Testing WITH RAG...")
        print("-"*60)
        for query in self.test_queries:
            result = self.run_test(agent_with_rag, query, "with_rag")
            results_with_rag.append(result)
        
        # Calculate metrics
        metrics = self.calculate_metrics(results_without_rag, results_with_rag)
        
        # Generate report
        report = self.generate_report(
            results_without_rag,
            results_with_rag,
            metrics
        )
        
        return {
            "results_without_rag": results_without_rag,
            "results_with_rag": results_with_rag,
            "metrics": metrics,
            "report": report
        }
    
    def calculate_metrics(
        self,
        results_without: List[Dict],
        results_with: List[Dict]
    ) -> Dict:
        """Calculate comparison metrics"""
        
        def avg(lst): return sum(lst) / len(lst) if lst else 0
        
        # Without RAG metrics
        without_scores = [r['validation_score'] for r in results_without]
        without_passed = sum(1 for r in results_without if r['validation_passed'])
        without_latency = [r['latency'] for r in results_without]
        
        # With RAG metrics
        with_scores = [r['validation_score'] for r in results_with]
        with_passed = sum(1 for r in results_with if r['validation_passed'])
        with_latency = [r['latency'] for r in results_with]
        
        return {
            "without_rag": {
                "avg_score": avg(without_scores),
                "pass_rate": without_passed / len(results_without),
                "avg_latency": avg(without_latency)
            },
            "with_rag": {
                "avg_score": avg(with_scores),
                "pass_rate": with_passed / len(results_with),
                "avg_latency": avg(with_latency)
            },
            "improvement": {
                "score_delta": avg(with_scores) - avg(without_scores),
                "pass_rate_delta": (with_passed - without_passed) / len(results_without),
                "latency_delta": avg(with_latency) - avg(without_latency)
            }
        }
    
    def generate_report(
        self,
        results_without: List[Dict],
        results_with: List[Dict],
        metrics: Dict
    ) -> str:
        """Generate formatted report"""
        
        report = []
        report.append("\n" + "="*60)
        report.append("RAG IMPACT ANALYSIS REPORT")
        report.append("="*60 + "\n")
        
        # Overall metrics
        report.append("OVERALL METRICS:")
        report.append("-"*60)
        report.append(f"{'Metric':<30} {'Without RAG':<15} {'With RAG':<15}")
        report.append("-"*60)
        
        w = metrics['without_rag']
        r = metrics['with_rag']
        i = metrics['improvement']
        
        report.append(f"{'Average Validation Score':<30} {w['avg_score']:<15.2f} {r['avg_score']:<15.2f}")
        report.append(f"{'Pass Rate (75%+ score)':<30} {w['pass_rate']*100:<14.1f}% {r['pass_rate']*100:<14.1f}%")
        report.append(f"{'Average Latency (seconds)':<30} {w['avg_latency']:<15.2f} {r['avg_latency']:<15.2f}")
        
        report.append("\nIMPROVEMENT:")
        report.append(f"  Score improvement: {i['score_delta']:+.2f} ({i['score_delta']/w['avg_score']*100:+.1f}%)")
        report.append(f"  Pass rate improvement: {i['pass_rate_delta']*100:+.1f}%")
        report.append(f"  Latency increase: {i['latency_delta']:+.2f}s ({i['latency_delta']/w['avg_latency']*100:+.1f}%)")
        
        # Per-query comparison
        report.append("\n" + "="*60)
        report.append("PER-QUERY RESULTS:")
        report.append("="*60 + "\n")
        
        for i, (without, with_rag) in enumerate(zip(results_without, results_with)):
            report.append(f"{i+1}. {without['question']}")
            report.append(f"   Category: {without['category']} | Complexity: {without['complexity']}")
            report.append(f"   Without RAG: Score {without['validation_score']:.2f} | {without['latency']:.2f}s")
            report.append(f"   With RAG:    Score {with_rag['validation_score']:.2f} | {with_rag['latency']:.2f}s")
            
            score_diff = with_rag['validation_score'] - without['validation_score']
            if score_diff > 0:
                report.append(f"   ✅ Improved by {score_diff:.2f}")
            elif score_diff < 0:
                report.append(f"   ⚠️  Degraded by {abs(score_diff):.2f}")
            else:
                report.append(f"   ➖ No change")
            
            if with_rag['missing_elements']:
                report.append(f"   Missing: {', '.join(with_rag['missing_elements'])}")
            
            report.append("")
        
        # Conclusion
        report.append("="*60)
        report.append("CONCLUSION:")
        report.append("="*60)
        
        if i['score_delta'] > 0.15:
            conclusion = "✅ RAG provides SIGNIFICANT improvement"
        elif i['score_delta'] > 0.05:
            conclusion = "✅ RAG provides MODERATE improvement"
        elif i['score_delta'] > 0:
            conclusion = "➖ RAG provides MINOR improvement"
        else:
            conclusion = "⚠️  RAG does not improve performance"
        
        report.append(conclusion)
        
        if i['latency_delta'] > 2:
            report.append("⚠️  Latency increase is significant (+2s)")
        else:
            report.append("✅ Latency increase is acceptable")
        
        report.append("\nRECOMMENDATION:")
        if i['score_delta'] > 0.1 and i['latency_delta'] < 3:
            report.append("✅ Deploy RAG enhancement to production")
        elif i['score_delta'] > 0.05:
            report.append("⚠️  Consider RAG for complex queries only")
        else:
            report.append("❌ RAG does not justify latency cost")
        
        report.append("="*60)
        
        return "\n".join(report)
    
    def save_results(self, results: Dict, filename: str = "rag_comparison.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to {filename}")


def main():
    """Run comparison test"""
    
    # Import agents
    try:
        from agent_with_rag import RAGAnalyticsAgent
    except ImportError:
        print("❌ Error: Cannot import RAGAnalyticsAgent")
        print("Make sure agent_with_rag.py is in the same directory")
        return
    
    # Initialize test
    test = RAGComparisonTest()
    
    # Initialize agents
    print("Initializing agents...")
    agent_without_rag = RAGAnalyticsAgent(
        db_path="saas_analytics.db",
        use_rag=False
    )
    
    agent_with_rag = RAGAnalyticsAgent(
        db_path="saas_analytics.db",
        use_rag=True,
        rag_k=5
    )
    
    # Run comparison
    results = test.run_comparison(agent_without_rag, agent_with_rag)
    
    # Print report
    print(results['report'])
    
    # Save results
    test.save_results(results)
    
    # Summary
    print("\n" + "="*60)
    print("Test complete! Results saved to rag_comparison.json")
    print("="*60)


if __name__ == "__main__":
    main()
