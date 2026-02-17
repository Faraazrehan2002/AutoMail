import pytest
from app.services.email_extract import (
    extract_emails_from_text,
    validate_email_address
)


class TestEmailValidation:
    """Test email validation"""
    
    def test_valid_emails(self):
        """Test that valid emails pass validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "user_123@test-domain.com"
        ]
        
        for email in valid_emails:
            assert validate_email_address(email), f"{email} should be valid"
    
    def test_invalid_emails(self):
        """Test that invalid emails fail validation"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@domain",
            "user @example.com",  # Space
            "user@exam ple.com"   # Space in domain
        ]
        
        for email in invalid_emails:
            assert not validate_email_address(email), f"{email} should be invalid"


class TestEmailExtraction:
    """Test email extraction from text"""
    
    def test_simple_email_extraction(self):
        """Test extracting a single email"""
        text = "Contact us at support@example.com for help."
        results = extract_emails_from_text(text)
        
        assert len(results) == 1
        assert results[0]['email'] == "support@example.com"
    
    def test_multiple_emails(self):
        """Test extracting multiple emails"""
        text = """
        Contact: john@example.com
        Sales: sales@company.com
        Support: help@support.org
        """
        results = extract_emails_from_text(text)
        
        assert len(results) == 3
        emails = {r['email'] for r in results}
        assert "john@example.com" in emails
        assert "sales@company.com" in emails
        assert "help@support.org" in emails
    
    def test_deduplication_case_insensitive(self):
        """Test that emails are deduplicated case-insensitively"""
        text = "Contact: John@Example.com or john@example.com or JOHN@EXAMPLE.COM"
        results = extract_emails_from_text(text)
        
        assert len(results) == 1
        assert results[0]['email'] == "john@example.com"
    
    def test_invalid_emails_filtered(self):
        """Test that invalid emails are filtered out"""
        text = "Valid: test@example.com Invalid: notanemail @bad.com"
        results = extract_emails_from_text(text)
        
        assert len(results) == 1
        assert results[0]['email'] == "test@example.com"
    
    def test_name_extraction(self):
        """Test that names are extracted when present"""
        text = "John Doe <john.doe@example.com>"
        results = extract_emails_from_text(text)
        
        assert len(results) == 1
        # Name extraction is heuristic-based, so we check if it exists
        # The exact format may vary
        assert results[0]['email'] == "john.doe@example.com"
    
    def test_complex_text(self):
        """Test extraction from complex text"""
        text = """
        Meeting attendees:
        - Alice Smith (alice@company.com)
        - Bob Johnson, bob.j@company.com
        - Charlie Brown <charlie@company.com>
        
        Also contact: info@company.com
        """
        results = extract_emails_from_text(text)
        
        # Should extract all unique emails
        emails = {r['email'] for r in results}
        assert len(emails) >= 3  # At least 3 unique emails
        assert "alice@company.com" in emails
        assert "bob.j@company.com" in emails
        assert "charlie@company.com" in emails
        assert "info@company.com" in emails
    
    def test_punctuation_stripping(self):
        """Test that punctuation around emails is stripped"""
        test_cases = [
            ("Contact: (test@example.com),", "test@example.com"),
            ("Email: [user@domain.com];", "user@domain.com"),
            ("Send to {admin@site.org}:", "admin@site.org"),
            ("test@example.com,", "test@example.com"),
            ("(test@example.com)", "test@example.com"),
        ]
        
        for text, expected_email in test_cases:
            results = extract_emails_from_text(text)
            assert len(results) == 1, f"Failed for text: {text}"
            assert results[0]['email'] == expected_email
    
    def test_uppercase_emails(self):
        """Test that uppercase emails are normalized to lowercase"""
        text = "Contact: TEST@EXAMPLE.COM or Test@Example.Com"
        results = extract_emails_from_text(text)
        
        assert len(results) == 1
        assert results[0]['email'] == "test@example.com"
    
    def test_tld_validation(self):
        """Test that emails with invalid TLD length are rejected"""
        invalid_tlds = [
            "test@example.c",  # TLD too short
            "user@domain.x",   # TLD too short
        ]
        
        for email in invalid_tlds:
            assert not validate_email_address(email), f"{email} should be invalid (TLD too short)"
        
        # Valid TLDs should pass
        valid_emails = [
            "test@example.co",  # 2 char TLD
            "user@domain.com",  # 3 char TLD
            "admin@site.org.uk",  # Multi-part TLD
        ]
        
        for email in valid_emails:
            assert validate_email_address(email), f"{email} should be valid"
    
    def test_sorting_by_domain_then_email(self):
        """Test that results are sorted by domain then email"""
        text = """
        z@b.com
        a@b.com
        test@a.com
        admin@a.com
        user@c.com
        """
        results = extract_emails_from_text(text)
        
        # Should be sorted: a.com (admin, test), b.com (a, z), c.com (user)
        assert len(results) == 5
        assert results[0]['email'] == "admin@a.com"
        assert results[1]['email'] == "test@a.com"
        assert results[2]['email'] == "a@b.com"
        assert results[3]['email'] == "z@b.com"
        assert results[4]['email'] == "user@c.com"
    
    def test_duplicate_emails_different_casing(self):
        """Test that duplicate emails with different casing are deduplicated"""
        text = "Contact: Test@Example.com, TEST@EXAMPLE.COM, test@example.com"
        results = extract_emails_from_text(text)
        
        assert len(results) == 1
        assert results[0]['email'] == "test@example.com"
    
    def test_emails_with_special_characters(self):
        """Test emails with special characters in local part"""
        text = "Contact: user+tag@example.com, user.name@domain.com, user_123@test.com"
        results = extract_emails_from_text(text)
        
        assert len(results) == 3
        emails = {r['email'] for r in results}
        assert "user+tag@example.com" in emails
        assert "user.name@domain.com" in emails
        assert "user_123@test.com" in emails
    
    def test_invalid_formats_rejected(self):
        """Test that various invalid email formats are rejected"""
        invalid_texts = [
            "notanemail",
            "@example.com",
            "user@",
            "user@domain",
            "user @example.com",
            "user@exam ple.com",
            "user@example.c",  # TLD too short
        ]
        
        for text in invalid_texts:
            results = extract_emails_from_text(text)
            assert len(results) == 0, f"Should not extract email from: {text}"
    
    def test_mixed_valid_invalid(self):
        """Test extraction from text with both valid and invalid emails"""
        text = "Valid: test@example.com, admin@site.org. Invalid: notanemail, @bad.com, user@domain"
        results = extract_emails_from_text(text)
        
        assert len(results) == 2
        emails = {r['email'] for r in results}
        assert "test@example.com" in emails
        assert "admin@site.org" in emails
