"""验证器测试"""



from auto_pm.delivery.verifier import CheckResult, DeliveryVerifier, VerificationReport


class TestVerificationReport:
    def test_approved(self):
        r = VerificationReport()
        r.add(CheckResult("D1", "ok", True, "test", "pass"))
        assert r.is_approved
        assert r.passed == 1

    def test_failed(self):
        r = VerificationReport()
        r.add(CheckResult("D1", "fail", False, "test"))
        assert not r.is_approved
        assert r.fail == 1

    def test_warn(self):
        r = VerificationReport()
        r.add(CheckResult("D1", "warn", True, "test", "warn"))
        assert r.is_approved
        assert r.warn == 1

    def test_summary(self):
        r = VerificationReport()
        r.add(CheckResult("D1", "ok", True, "test", "pass"))
        s = r.summary()
        assert "PASS" in s


class TestDeliveryVerifier:
    def test_no_exe(self, tmp_path):
        d = tmp_path / "delivery"
        d.mkdir()
        v = DeliveryVerifier()
        report = v.verify_delivery_dir(d)
        assert not report.is_approved

    def test_zip_missing(self, tmp_path):
        v = DeliveryVerifier()
        report = v.verify_zip(tmp_path / "nonexistent.zip")
        assert not report.is_approved
