import os
import tempfile
import pytest
from auto_pm.core.prototype_service import PrototypeService

def test_prototype_init_and_bundle():
    with tempfile.TemporaryDirectory() as tmp_dir:
        service = PrototypeService(tmp_dir)
        
        # Test init
        init_res = service.init(tmp_dir, template="hmi")
        assert init_res.success is True
        assert os.path.exists(init_res.output_path)
        
        # Test bundle
        bundle_res = service.bundle(tmp_dir, version="V1.0.0")
        assert bundle_res.success is True
        assert os.path.exists(bundle_res.output_path)
        assert "V1.0.0" in bundle_res.output_path

def test_prototype_check():
    with tempfile.TemporaryDirectory() as tmp_dir:
        service = PrototypeService(tmp_dir)
        service.init(tmp_dir, template="hmi")
        
        check_res = service.check(tmp_dir)
        assert check_res.passed is True
        assert len(check_res.errors) == 0
