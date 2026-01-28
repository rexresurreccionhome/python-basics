import random
import statistics
import ipaddress
from abc import ABC, abstractmethod
from typing import Self

from fraud_detection_system.models import FraudRecord


class FraudAnalysisError(Exception):
    pass


class FraudAnalysis(ABC):
    _fraud_record: FraudRecord

    def __init__(self, fraud_record: FraudRecord) -> None:
        self._fraud_record = fraud_record

    @property
    def fraud_record(self) -> FraudRecord:
        return self._fraud_record

    @abstractmethod
    def assess_risk(self) -> float:
        pass


class IPAddressFraudAnalysis(FraudAnalysis):
    @staticmethod
    def valid_ip_address(ip_address: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        try:
            return ipaddress.ip_address(ip_address)
        except ValueError:
            raise FraudAnalysisError("Invalid IP address format")

    @abstractmethod
    def assess_risk(self) -> float:
        pass


class IPAddressRecordFraudAnalysis(IPAddressFraudAnalysis):
    def assess_risk(self) -> float:
        ip_address = self.valid_ip_address(self.fraud_record.device_info.ip_address)
        # Dummy logic for assessing risk based on IP address record
        print(f"Checking IP address record: {ip_address}")
        return random.uniform(0, 1) # Dummy score


class GeoIPAddressFraudAnalysis(IPAddressFraudAnalysis):
    def assess_risk(self) -> float:
        ip_address = self.valid_ip_address(self.fraud_record.device_info.ip_address)
        # Dummy logic for assessing risk based on geolocation of IP address
        print(f"Geolocating IP address: {ip_address}")
        return random.uniform(0, 1) # Dummy score


class EmailDomainFraudAnalysis(FraudAnalysis):
    @staticmethod
    def get_domain(email: str) -> str:
        return email.split('@')[1]

    @abstractmethod
    def assess_risk(self) -> float:
        pass


class FreeEmailDomainFraudAnalysis(EmailDomainFraudAnalysis):
    def assess_risk(self) -> float:
        domain = self.get_domain(self.fraud_record.personal_info.email)
        # Dummy logic for assessing risk based on free email domain
        print(f"Checking free email domain: {domain}")
        return random.uniform(0, 1) # Dummy score


class DarkWebEmailDomainFraudAnalysis(EmailDomainFraudAnalysis):
    def assess_risk(self) -> float:
        domain = self.get_domain(self.fraud_record.personal_info.email)
        # Dummy logic for assessing risk based on dark web email domain
        print(f"Checking dark web email domain: {domain}")
        return random.uniform(0, 1) # Dummy score


class SpamRecordPhoneNumberFraudAnalysis(FraudAnalysis):
    def assess_risk(self) -> float:
        # Dummy logic for assessing risk based on spam phone number record
        print(f"Checking spam phone number record: {self.fraud_record.personal_info.phone_number}")
        return random.uniform(0, 1) # Dummy score


class FraudAnalyzer(ABC):
    @abstractmethod
    def risk_assessments(self, fraud_record: FraudRecord) -> list[FraudAnalysis]:
        pass

    def assess_risks(self, fraud_record: FraudRecord) -> dict[str, float]:
        assessment_scores = []
        for assessment in self.risk_assessments(fraud_record):
            assessment_scores.append(
                assessment.assess_risk()
            )

        return {self.__class__.__name__: self._summarize_risk_scores(assessment_scores)}

    def _summarize_risk_scores(self, assessment_scores: list[float]) -> float:
        if assessment_scores:
            return statistics.mean(assessment_scores)
        
        return 0.0


class IPAddressFraudAnalyzer(FraudAnalyzer):
    def risk_assessments(self, fraud_record: FraudRecord) -> list[FraudAnalysis]:
        return [
            IPAddressRecordFraudAnalysis(fraud_record),
            GeoIPAddressFraudAnalysis(fraud_record),
        ]


class EmailDomainFraudAnalyzer(FraudAnalyzer):
    def risk_assessments(self, fraud_record: FraudRecord) -> list[FraudAnalysis]:
        return [
            FreeEmailDomainFraudAnalysis(fraud_record),
            DarkWebEmailDomainFraudAnalysis(fraud_record),
        ]


class PhoneNumberFraudAnalyzer(FraudAnalyzer):
    def risk_assessments(self, fraud_record: FraudRecord) -> list[FraudAnalysis]:
        return [
            SpamRecordPhoneNumberFraudAnalysis(fraud_record),
        ]


class FraudAnalysisHandler(ABC):
    _next_handler: Self | None

    def __init__(self, fraud_analyzer: FraudAnalyzer) -> None:
        self._next_handler = None
        self._fraud_analyzer = fraud_analyzer
    
    @property
    def next_handler(self) -> Self | None:
        return self._next_handler

    def set_next_handler(self, handler: Self) -> Self:
        self._next_handler = handler
        return handler

    @property
    def fraud_analyzer(self) -> FraudAnalyzer:
        return self._fraud_analyzer

    def handle(self, fraud_record: FraudRecord, analysis: dict[str, float]) -> dict[str, float]:
        # Pass to the next handler in the chain if exists, otherwise return the final analysis
        if self.next_handler:
            return self.next_handler.handle(fraud_record, analysis=analysis)
        
        return analysis

    def start_handling(self, fraud_record: FraudRecord) -> dict[str, float]:
        return self.handle(fraud_record, analysis={})


class DefaultAnalysisHandler(FraudAnalysisHandler):
    def handle(self, fraud_record: FraudRecord, analysis: dict[str, float]) -> dict[str, float]:
        # This will always perform risk assessment on device info
        analysis.update(self.fraud_analyzer.assess_risks(fraud_record))

        return super().handle(fraud_record, analysis)

class EmailAnalysisHandler(FraudAnalysisHandler):
    RISK_THRESHOLD = 0.7

    def handle(self, fraud_record: FraudRecord, analysis: dict[str, float]) -> dict[str, float]:
        # Demo logic to short-circuit if risk is above threshold
        if fraud_record.personal_info.email:
            email_analysis = self.fraud_analyzer.assess_risks(fraud_record)
            analysis.update(email_analysis)
            if statistics.mean(email_analysis.values()) > self.RISK_THRESHOLD:
                return analysis

        return super().handle(fraud_record, analysis=analysis)


class PhoneNumberAnalysisHandler(FraudAnalysisHandler):
    RISK_THRESHOLD = 0.5

    def handle(self, fraud_record: FraudRecord, analysis: dict[str, float]) -> dict[str, float]:
        # Demo logic to short-circuit if risk is above threshold
        if fraud_record.personal_info.phone_number:
            phone_analysis = self.fraud_analyzer.assess_risks(fraud_record)
            analysis.update(phone_analysis)
            if statistics.mean(phone_analysis.values()) > self.RISK_THRESHOLD:
                return analysis

        return super().handle(fraud_record, analysis=analysis)


class FraudAnalysisService:
    # The service wraps the complexity of setting up the chain of responsibility
    # and provides a simple interface for analyzing fraud records.
    def analyze_fraud_record(self, fraud_record: FraudRecord) -> dict[str, float]:
        # Setting up the chain of responsibility
        ip_address_handler = DefaultAnalysisHandler(IPAddressFraudAnalyzer())
        email_handler = EmailAnalysisHandler(EmailDomainFraudAnalyzer())
        phone_handler = PhoneNumberAnalysisHandler(PhoneNumberFraudAnalyzer())
        ip_address_handler.set_next_handler(email_handler).set_next_handler(phone_handler)

        return ip_address_handler.start_handling(fraud_record)