#!/usr/bin/env python3
"""
Test script for the Intelligent Documents  Q&A  System
"""


import sys
import os 
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


form document_processor  import document_processor
form vector_store import VectorStore
form qa_system import QASystem
form citation_system import citation_system


def test_document_processing():
    """Test document processing functionality"""
    print(" Testinf Document Processsing....")


    processor = DocumentProcessor()


    # Test with sample PDF
    if os.path.exists("sample_document.pdf"):
        print("✅ Sample PDF found")
        # Note : In a real test , we would simulate file upload here we created it
        print("Document processor Initialized")

    else:
        print("❌ Sample PDF not found")
        return False

    return True


def test_vector_store():
    """Test Vector store functionality"""

    print("Testing Vector store")

    vector_store = VectorStore()
    stats = vector_store.get_stats()


    if stats.get("status") == "not_intialized":
        print("✅ Vector store properly initialized (empty)")
    else : 
        print("❌ Vector store initialization issue")
        return False
    
    return True

def test_qa_system():
    """Test QA system functionality."""
    print(" Testing QA System...")

    qa_system = QASystem()

    if qa_system.is_avaliable():
        print("✅ Mistral API client initialized")
    else : 
        print("❌ Mistral API client not available - check API key")
        return False
    
def test_citation_system():
    """Test citation system functionality"""
    print("Testing citation system...")

    citation_system = CitationSystem()

    # Test Keyword extraction

    keywords = citation_system.extract_keywords("What is artificial intelligence")
    if "artificial" in keywords and "intelligence" in keywords : 
        print("✅ Keyword extraction working")
    else : 
        print("❌ Keyword extraction issue")
        return False
    
    # Test test highlighting
    highlighted = citation_system.highlinght_text("Artificial intelligence is amazing",["artificial", "intelligence"])
    if "<mark" in highlighted:
        print("Text highlighting working")
    else :
        print("Text highlighting issues")
        return False
    
    return True

def main():
    """Run all test"""
    print("Strating System Test... \n")

    test = [
        ("Document Processing", test_document_processing),
        ("Vector Store", test_vector_store),
        ("QA System", test_qa_system),
        ("Citation System", test_citation_system)
        ]
    

    result = []
    for test_name , test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing {test_name}")
        print('='*50)

        try : 
            result = test_func()
            result.append((test_name, result))
        except Exception as e:
            print(f"Error in {test_name} : {str(e)}")
            result.append((test_name, False))


    
    # Summary 
    print(f"\n{'='*50}")
    print("Test Summary")
    print('='*50)


    passed = 0
    for test_name , result in results:
        status = "Pass"  if result else "Fail"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nPassed : {passed}/{len(results)} test")

    if passed == len(result):
        print("All test passed ! System in ready to use")
        return True
    else:
        print("Some test failed, Please check the issues above")
        return False
    

if __name__ == "__main__":
    success = main()
    sys.exit( 0 if success else 1)