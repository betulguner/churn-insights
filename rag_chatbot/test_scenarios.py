"""
Test Scenarios for RAG Chatbot
Sample questions and expected responses for testing the chatbot functionality
"""

import os
import sys
from typing import List, Dict, Any

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.rag_pipeline import RAGPipeline

class TestScenarios:
    """Test scenarios for the RAG chatbot"""
    
    def __init__(self):
        self.test_questions = [
            # Customer Overview Questions
            {
                "question": "How many customers do we have?",
                "category": "CUSTOMER_OVERVIEW",
                "expected_elements": ["total_customers", "COUNT"],
                "description": "Basic customer count query"
            },
            {
                "question": "What's our total customer count?",
                "category": "CUSTOMER_OVERVIEW", 
                "expected_elements": ["COUNT(*)", "customer"],
                "description": "Alternative phrasing for customer count"
            },
            {
                "question": "Show me customer demographics",
                "category": "CUSTOMER_OVERVIEW",
                "expected_elements": ["gender", "senior_citizen", "GROUP BY"],
                "description": "Customer demographic breakdown"
            },
            
            # Churn Analysis Questions
            {
                "question": "What's our churn rate?",
                "category": "CHURN_ANALYSIS",
                "expected_elements": ["churn_rate", "churn_status", "percentage"],
                "description": "Overall churn rate calculation"
            },
            {
                "question": "How many customers churned?",
                "category": "CHURN_ANALYSIS",
                "expected_elements": ["churn_status = true", "COUNT"],
                "description": "Count of churned customers"
            },
            {
                "question": "Show me churn rate by contract type",
                "category": "CHURN_ANALYSIS",
                "expected_elements": ["contract", "GROUP BY", "churn_rate"],
                "description": "Churn analysis by contract type"
            },
            
            # Segment Analysis Questions
            {
                "question": "What's the churn rate by customer segment?",
                "category": "SEGMENT_ANALYSIS",
                "expected_elements": ["segment_name", "GROUP BY", "churn_rate"],
                "description": "Churn rate by customer segments"
            },
            {
                "question": "Show me high-value customers",
                "category": "SEGMENT_ANALYSIS",
                "expected_elements": ["total_charges", "ORDER BY", "DESC"],
                "description": "High-value customer identification"
            },
            {
                "question": "Which segment has the highest churn?",
                "category": "SEGMENT_ANALYSIS",
                "expected_elements": ["segment_name", "churn_rate", "ORDER BY"],
                "description": "Highest churn segment identification"
            },
            
            # Revenue Analysis Questions
            {
                "question": "What's the average monthly charges?",
                "category": "REVENUE_ANALYSIS",
                "expected_elements": ["AVG", "monthly_charges"],
                "description": "Average monthly charges calculation"
            },
            {
                "question": "Show me revenue by customer segment",
                "category": "REVENUE_ANALYSIS",
                "expected_elements": ["segment_name", "total_charges", "GROUP BY"],
                "description": "Revenue analysis by segment"
            },
            {
                "question": "What's the total revenue?",
                "category": "REVENUE_ANALYSIS",
                "expected_elements": ["SUM", "total_charges"],
                "description": "Total revenue calculation"
            },
            
            # Service Analysis Questions
            {
                "question": "What's the most popular internet service?",
                "category": "SERVICE_ANALYSIS",
                "expected_elements": ["internet_service", "COUNT", "GROUP BY"],
                "description": "Internet service popularity"
            },
            {
                "question": "Show me churn rate by internet service",
                "category": "SERVICE_ANALYSIS",
                "expected_elements": ["internet_service", "churn_rate", "GROUP BY"],
                "description": "Churn analysis by internet service"
            },
            {
                "question": "How many customers have phone service?",
                "category": "SERVICE_ANALYSIS",
                "expected_elements": ["phone_service", "COUNT", "WHERE"],
                "description": "Phone service customer count"
            },
            
            # Trend Analysis Questions
            {
                "question": "Show me churn trends over time",
                "category": "TREND_ANALYSIS",
                "expected_elements": ["DATE_TRUNC", "month", "GROUP BY"],
                "description": "Time-based churn trends"
            },
            {
                "question": "What's the monthly churn rate?",
                "category": "TREND_ANALYSIS",
                "expected_elements": ["month", "churn_rate", "ORDER BY"],
                "description": "Monthly churn rate analysis"
            },
            
            # Comparison Analysis Questions
            {
                "question": "Compare churn rates between contract types",
                "category": "COMPARISON_ANALYSIS",
                "expected_elements": ["contract", "churn_rate", "GROUP BY"],
                "description": "Contract type comparison"
            },
            {
                "question": "Which segment performs better?",
                "category": "COMPARISON_ANALYSIS",
                "expected_elements": ["segment_name", "churn_rate", "ORDER BY"],
                "description": "Segment performance comparison"
            },
            
            # Specific Customer Questions
            {
                "question": "Show me customer ID 1234 details",
                "category": "SPECIFIC_CUSTOMER",
                "expected_elements": ["customer_id = 1234", "WHERE"],
                "description": "Specific customer lookup"
            },
            
            # Complex Questions
            {
                "question": "Show me customers with high monthly charges but low churn risk",
                "category": "OTHER",
                "expected_elements": ["monthly_charges", "churn_status", "WHERE"],
                "description": "Complex filtering query"
            },
            {
                "question": "What's the average tenure for churned customers?",
                "category": "CHURN_ANALYSIS",
                "expected_elements": ["AVG", "tenure_months", "churn_status = true"],
                "description": "Average tenure for churned customers"
            }
        ]
    
    def run_test_scenarios(self, pipeline: RAGPipeline) -> List[Dict[str, Any]]:
        """
        Run all test scenarios and collect results
        
        Args:
            pipeline: Initialized RAG pipeline
            
        Returns:
            List of test results
        """
        results = []
        
        print("🧪 Running RAG Chatbot Test Scenarios")
        print("=" * 60)
        
        for i, test_case in enumerate(self.test_questions, 1):
            print(f"\n[{i}/{len(self.test_questions)}] Testing: {test_case['question']}")
            print(f"Category: {test_case['category']}")
            print(f"Description: {test_case['description']}")
            
            try:
                # Process the question
                response = pipeline.process_question(test_case['question'])
                
                # Analyze the response
                test_result = {
                    "question": test_case['question'],
                    "expected_category": test_case['category'],
                    "actual_category": response.get('category', 'UNKNOWN'),
                    "success": response.get('success', False),
                    "sql_query": response.get('sql_query', ''),
                    "response": response.get('formatted_response', ''),
                    "error": response.get('error'),
                    "expected_elements": test_case['expected_elements'],
                    "sql_contains_expected": self._check_sql_elements(
                        response.get('sql_query', ''), 
                        test_case['expected_elements']
                    )
                }
                
                results.append(test_result)
                
                # Print results
                if test_result['success']:
                    print("✅ SUCCESS")
                    print(f"Category Match: {test_result['actual_category'] == test_result['expected_category']}")
                    print(f"SQL Elements: {test_result['sql_contains_expected']}")
                    print(f"SQL: {test_result['sql_query'][:100]}...")
                else:
                    print("❌ FAILED")
                    print(f"Error: {test_result['error']}")
                
            except Exception as e:
                print(f"❌ EXCEPTION: {e}")
                results.append({
                    "question": test_case['question'],
                    "expected_category": test_case['category'],
                    "actual_category": "ERROR",
                    "success": False,
                    "sql_query": "",
                    "response": "",
                    "error": str(e),
                    "expected_elements": test_case['expected_elements'],
                    "sql_contains_expected": False
                })
            
            print("-" * 40)
        
        return results
    
    def _check_sql_elements(self, sql_query: str, expected_elements: List[str]) -> Dict[str, bool]:
        """
        Check if SQL query contains expected elements
        
        Args:
            sql_query: Generated SQL query
            expected_elements: List of expected SQL elements
            
        Returns:
            Dictionary mapping elements to their presence
        """
        sql_upper = sql_query.upper()
        results = {}
        
        for element in expected_elements:
            results[element] = element.upper() in sql_upper
        
        return results
    
    def generate_test_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a test report
        
        Args:
            results: List of test results
            
        Returns:
            Formatted test report
        """
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        category_matches = sum(1 for r in results if r['actual_category'] == r['expected_category'])
        
        report = f"""
# RAG Chatbot Test Report

## Summary
- **Total Tests**: {total_tests}
- **Successful Tests**: {successful_tests} ({successful_tests/total_tests*100:.1f}%)
- **Category Matches**: {category_matches} ({category_matches/total_tests*100:.1f}%)

## Detailed Results

"""
        
        for i, result in enumerate(results, 1):
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            category_match = "✅" if result['actual_category'] == result['expected_category'] else "❌"
            
            report += f"""
### Test {i}: {result['question'][:50]}...

**Status**: {status}
**Expected Category**: {result['expected_category']}
**Actual Category**: {result['actual_category']} {category_match}
**Success**: {result['success']}

**SQL Query**:
```sql
{result['sql_query']}
```

**Response**:
{result['response'][:200]}...

**SQL Elements Check**:
"""
            for element, present in result['sql_contains_expected'].items():
                status_icon = "✅" if present else "❌"
                report += f"- {element}: {status_icon}\n"
            
            if result['error']:
                report += f"\n**Error**: {result['error']}\n"
            
            report += "\n---\n"
        
        return report

# Example usage
if __name__ == "__main__":
    try:
        # Initialize RAG pipeline
        pipeline = RAGPipeline()
        
        # Initialize test scenarios
        test_scenarios = TestScenarios()
        
        # Run tests
        results = test_scenarios.run_test_scenarios(pipeline)
        
        # Generate report
        report = test_scenarios.generate_test_report(results)
        
        # Save report
        with open('rag_chatbot/test_report.md', 'w') as f:
            f.write(report)
        
        print(f"\n📊 Test Report Generated: rag_chatbot/test_report.md")
        print(f"Success Rate: {sum(1 for r in results if r['success'])/len(results)*100:.1f}%")
        
    except Exception as e:
        print(f"Test execution failed: {e}")
