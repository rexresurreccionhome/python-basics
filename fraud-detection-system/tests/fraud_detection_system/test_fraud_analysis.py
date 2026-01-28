from fraud_detection_system.fraud_analysis import (
    IPAddressRecordFraudAnalysis,
    GeoIPAddressFraudAnalysis,
    FreeEmailDomainFraudAnalysis,
    DarkWebEmailDomainFraudAnalysis,
    SpamRecordPhoneNumberFraudAnalysis,
    FraudAnalyzer,
    IPAddressFraudAnalyzer,
    EmailDomainFraudAnalyzer,
    PhoneNumberFraudAnalyzer,
)
from tests.fraud_detection_system.builder import FraudRecordBuilder


class TestIPAddressRecordFraudAnalysis:
    def test_assess_risk__with_valid_ipv4__returns_risk_score(self, mocker):
        mocker.patch(
            "fraud_detection_system.fraud_analysis.random.uniform", return_value=0.75
        )
        fraud_analysis = IPAddressRecordFraudAnalysis(
            fraud_record=FraudRecordBuilder().build()
        )
        risk_score = fraud_analysis.assess_risk()
        assert risk_score == 0.75


class TestGeoIPAddressFraudAnalysis:
    def test_assess_risk__with_valid_ipv4__returns_risk_score(self, mocker):
        mocker.patch(
            "fraud_detection_system.fraud_analysis.random.uniform", return_value=0.75
        )
        fraud_analysis = GeoIPAddressFraudAnalysis(
            fraud_record=FraudRecordBuilder().build()
        )
        risk_score = fraud_analysis.assess_risk()
        assert risk_score == 0.75


class TestFreeEmailDomainFraudAnalysis:
    def test_assess_risk__with_email_address__returns_risk_score(self, mocker):
        mocker.patch(
            "fraud_detection_system.fraud_analysis.random.uniform", return_value=0.75
        )
        fraud_analysis = FreeEmailDomainFraudAnalysis(
            fraud_record=FraudRecordBuilder().build()
        )
        risk_score = fraud_analysis.assess_risk()
        assert risk_score == 0.75


class TestDarkWebEmailDomainFraudAnalysis:
    def test_assess_risk__with_email_address__returns_risk_score(self, mocker):
        mocker.patch(
            "fraud_detection_system.fraud_analysis.random.uniform", return_value=0.75
        )
        fraud_analysis = DarkWebEmailDomainFraudAnalysis(
            fraud_record=FraudRecordBuilder().build()
        )
        risk_score = fraud_analysis.assess_risk()
        assert risk_score == 0.75


class TestSpamRecordPhoneNumberFraudAnalysis:
    def test_assess_risk__with_email_address__returns_risk_score(self, mocker):
        mocker.patch(
            "fraud_detection_system.fraud_analysis.random.uniform", return_value=0.75
        )
        fraud_analysis = SpamRecordPhoneNumberFraudAnalysis(
            fraud_record=FraudRecordBuilder().build()
        )
        risk_score = fraud_analysis.assess_risk()
        assert risk_score == 0.75


class TestFraudAnalyzer:
    def test_assess_risks__mock_risk_assessments__returns_risk_scores(self, mocker):
        mock_analysis_instances = [
            mocker.MagicMock(
                assess_risk=mocker.MagicMock(return_value=0.2)
            ),
            mocker.MagicMock(
                assess_risk=mocker.MagicMock(return_value=0.8)
            ),
        ]
        class MockFraudAnalyzer(FraudAnalyzer):
            def risk_assessments(
                self, fraud_record
            ):
                return mock_analysis_instances
        
        fraud_analyzer = MockFraudAnalyzer()
        risk_scores = fraud_analyzer.assess_risks(
            fraud_record=FraudRecordBuilder().build()
        )
        assert risk_scores == {"MockFraudAnalyzer": 0.5}



class TestFraudAnalyzer:
    def test_assess_risks__mock_risk_assessments__returns_risk_scores(self, mocker):
        mock_analysis_instances = [
            mocker.MagicMock(
                assess_risk=mocker.MagicMock(return_value=0.2)
            ),
            mocker.MagicMock(
                assess_risk=mocker.MagicMock(return_value=0.8)
            ),
        ]
        class MockFraudAnalyzer(FraudAnalyzer):
            def risk_assessments(
                self, fraud_record
            ):
                return mock_analysis_instances
        
        fraud_analyzer = MockFraudAnalyzer()
        risk_scores = fraud_analyzer.assess_risks(
            fraud_record=FraudRecordBuilder().build()
        )
        assert risk_scores == {"MockFraudAnalyzer": 0.5}


class TestIPAddressFraudAnalyzer:
    def test_risk_assessments__with_fraud_record__returns_fraud_analysis(self):
        fraud_analyzer = IPAddressFraudAnalyzer()
        fraud_analysis = fraud_analyzer.risk_assessments(
            fraud_record=FraudRecordBuilder().build()
        )
        assert len(fraud_analysis) == 2
        assert isinstance(fraud_analysis[0], IPAddressRecordFraudAnalysis)
        assert isinstance(fraud_analysis[1], GeoIPAddressFraudAnalysis)


class TestEmailDomainFraudAnalyzer:
    def test_risk_assessments__with_fraud_record__returns_fraud_analysis(self):
        fraud_analyzer = EmailDomainFraudAnalyzer()
        fraud_analysis = fraud_analyzer.risk_assessments(
            fraud_record=FraudRecordBuilder().build()
        )
        assert len(fraud_analysis) == 2
        assert isinstance(fraud_analysis[0], FreeEmailDomainFraudAnalysis)
        assert isinstance(fraud_analysis[1], DarkWebEmailDomainFraudAnalysis)


class TestPhoneNumberFraudAnalyzer:
    def test_risk_assessments__with_fraud_record__returns_fraud_analysis(self):
        fraud_analyzer = PhoneNumberFraudAnalyzer()
        fraud_analysis = fraud_analyzer.risk_assessments(
            fraud_record=FraudRecordBuilder().build()
        )
        assert len(fraud_analysis) == 1
        assert isinstance(fraud_analysis[0], SpamRecordPhoneNumberFraudAnalysis)